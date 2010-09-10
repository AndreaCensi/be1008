import cPickle as pickle
import numpy
from numpy import nonzero
import os

from reprep import Node
from reprep.out.html import node_to_html_document
from be1008.camera_figure import camera_figures
from be1008.utils import my_pickle_load, my_pickle_dump


def main():
    """
    Prepare data with: ::
    
        be_average_logs_results --dir . --experiment camera_bgds_boot -v gray/GI_DI -v contrast/GS_DS
        be_average_logs_results --dir . --experiment camera_bgds_stats -v gray/GI_DI -v contrast/GS_DS
        

    Reads: ::
    
        out/average_logs_results/camera_bgds_boot.pickle
        out/average_logs_results/camera_bgds_stats.pickle
        
    Writes: ::
    
        out/camera_bgds_boot/report.html
        out/camera_bgds_boot/report.pickle
        out/camera_bgds_boot/<variant>:G.pickle 
        
    moreover, it calls camera_figures() that creates
    
         output_pattern = 'out/camera_figures/{variant}.tex'
     
        
    """
    input1 = 'out/average_logs_results/camera_bgds_boot.pickle'
    input2 = 'out/average_logs_results/camera_bgds_stats.pickle'
    variant_pattern = "out/camera_bgds_boot/{variant}:G.pickle"
    out_html = 'out/camera_bgds_boot/report.html'
    out_pickle = 'out/camera_bgds_boot/report.pickle'
    
    results = my_pickle_load(input1)

    stats = my_pickle_load(input2)
    
    print "Creating report..."
    
    
    report = Node('camera_bgds_boot') 
    
    k = 1
    variants = sorted(results.keys())
    for variant_id in variants:
        
        
        data = results[variant_id] 
        data2 = stats[variant_id]
        print data2.keys()
        variant = variant_id.replace('/', '_')
        print 'Considering %s' % variant
        
        #if not variant in ['gray_GI_DI', 'contrast_GS_DS']:
        #    continue
        
        n = report.node(variant)
        f1 = n.figure('value')
        f2 = n.figure('sign')
        f3 = n.figure('abs')
        
        for variable, value in data.items():
            v = n.data(variable, value)
            if len(value.shape) == 3:
                f1.sub(variable, display='rgb')
            else:
                v.data('sign', numpy.sign(value), desc='sign of %s' % variable)
                v.data('abs', numpy.abs(value), desc='abs of %s' % variable)
                f1.sub(variable, display='posneg', skim=1)
                f2.sub('%s/sign' % variable, display='posneg')
                f3.sub('%s/abs' % variable, display='scale', min_value=0)
        
    
        f4 = n.figure('stats')

        for variable, value in data2.items():
            v = n.data(variable, value)
            f4.sub(variable, display='scale', skim=1)

        Gxl = data['Gxl']
        Gyl = data['Gyl']
        Gxa = data['Gxa']
        Gya = data['Gya'] 
        
        
        def set_zeros_to_one(x):
            x = x.copy()
            zeros, = nonzero(x.flat == 0)
            x.flat[zeros] = 1
            print "%d/%d of data were 0" % (len(zeros), len(x.flat))
            return x
        
        norm_gx = set_zeros_to_one (data2['gx_abs']) 
        norm_gy = set_zeros_to_one (data2['gy_abs'])  

        Gxl_norm = Gxl / norm_gx
        Gyl_norm = Gyl / norm_gy
        Gxa_norm = Gxa / norm_gx
        Gya_norm = Gya / norm_gy

        
        n.data('Gxl_norm', Gxl_norm)
        n.data('Gyl_norm', Gyl_norm)
        n.data('Gxa_norm', Gxa_norm)
        n.data('Gya_norm', Gya_norm)

        
        f5 = n.figure('normalized')
        display = {'display': 'posneg', 'skim': 2}
        f5.sub('Gxl_norm', **display)
        f5.sub('Gyl_norm', **display)
        f5.sub('Gxa_norm', **display)
        f5.sub('Gya_norm', **display)
        
        k += 1
        if k > 1:
            pass
        #   break # tmp
             
        if True:
            s = {'variant': variant,
                 'Gxl':Gxl_norm,
                 'Gyl':Gyl_norm,
                 'Gxa':Gxa_norm,
                 'Gya':Gya_norm }
            filename = variant_pattern.format(variant=variant)
            dir = os.path.dirname(filename)
            if not os.path.exists(dir):
                os.makedirs(dir)
            pickle.dump(s, open(filename, 'wb'))
            print 'Written on %s' % filename
            
    
    print "Writing on %s" % out_html
    node_to_html_document(report, out_html)
    #print "Writing on %s" % out_pickle
    my_pickle_dump(report, out_pickle)
    camera_figures(report)
    
if __name__ == '__main__':
    main()
