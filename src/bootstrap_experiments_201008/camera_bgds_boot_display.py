import cPickle as pickle
from reprep.node import Node
from reprep.out.html import node_to_html_document
import numpy
from numpy import nonzero
import os

def camera_bgds_boot_display():
    """
    Prepare data with:
    
        average_logs_results --dir . --experiment camera_bgds_boot
        average_logs_results --dir . --experiment camera_bgds_stats
    
    """
    print "Loading first..."
    results = pickle.load(open('camera_bgds_boot.pickle', 'rb'))
    print "Loading second..."
    stats = pickle.load(open('camera_bgds_stats.pickle', 'rb'))
    print "Creating report..."
    
    
    report = Node('camera_bgds_boot') 
    
    k = 1
    variants = sorted(results.keys())
    for variant in variants:
        data = results[variant] 
        print 'Considering %s' % variant
        
        n = report.node(variant)
        f1 = n.figure('value')
        f2 = n.figure('sign')
        f3 = n.figure('abs')
        
        for variable, value in data.items():
            v = n.data(variable, value)
            v.data('sign', numpy.sign(value), desc='sign of %s' % variable)
            v.data('abs', numpy.abs(value), desc='abs of %s' % variable)
            f1.sub(variable, display='posneg')
            f2.sub('%s/sign' % variable, display='posneg')
            f3.sub('%s/abs' % variable, display='scale', min_value=0)
        
    
        f4 = n.figure('stats')

        data2 = stats[variant]
        for variable, value in data2.items():
            v = n.data(variable, value)
            
            f4.sub(variable, display='scale')

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
        if k > 2:
            pass
            # break
            
            
        #if variant == 'gray/GS_DS':
        if True:
            s = {'variant': variant,
                 'Gxl':Gxl_norm,
                 'Gyl':Gyl_norm,
                 'Gxa':Gxa_norm,
                 'Gya':Gya_norm }
            filename = "out/camera_bgds_boot/%s:G.pickle" % variant.replace('/', '_')
            dir = os.path.dirname(filename)
            if not os.path.exists(dir):
                os.makedirs(dir)
            pickle.dump(s, open(filename, 'wb'))
            print 'Written on %s' % filename
    
    node_to_html_document(report, 'camera_bgds_boot.html')

if __name__ == '__main__':
    camera_bgds_boot_display()
