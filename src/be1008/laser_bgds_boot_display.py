import numpy, math, os
from numpy import  abs, cos, sin, linspace

from matplotlib import rc
rc('font', **{'family':'serif'})

from procgraph.core.model_loadsave import make_sure_dir_exists
from reprep import Node
from reprep.out.html import node_to_html_document # XXX:
from reprep.out.platex import Latex, makecmd

from .camera_figure import makelabel, write_graphics
from .utils import my_pickle_load, my_pickle_dump


def my_figures(results):
    r = Node('myfigures')
    sick_indices = range(342, 704)
    N = len(sick_indices)
    theta = linspace(0, 2 * math.pi, N) - math.pi / 2
    
    theta_deg = theta * 180 / math.pi
    
    variants = ['GI_DI', 'GS_DS']
    xlabel = 'ray direction (deg)'
    ylabel = 'normalized tensor (unitless)'
    
    
    a = 0.9
    figparams = { 'mime': 'application/pdf', 'figsize': (4 * a, 3 * a) }
    
    def adjust_axes(pylab):
        # left, bottom, right, top
        #borders = [0.15, 0.15, 0.03, 0.05]
        borders = [0.2, 0.17, 0.05, 0.05]
        w = 1 - borders[0] - borders[2]
        h = 1 - borders[1] - borders[3]
        pylab.axes([borders[0], borders[1], w, h])
        
    def set0axis(pylab):
        a = pylab.axis()
        pylab.axis([-91, +271, 0, a[3]])
        pylab.xticks([-90, 0, 90, 180, 270])
        
    with r.data_pylab('report_y_mean', **figparams) as pylab:
        adjust_axes(pylab)
        pylab.plot(theta_deg, results[variants[0]]['y_mean'][sick_indices], 'k-')
        pylab.xlabel(xlabel)
        pylab.ylabel('distance (m)')
        set0axis(pylab)

    with r.data_pylab('report_y_var', **figparams) as pylab:
        adjust_axes(pylab)
        var = results[variants[0]]['y_var'][sick_indices]
        pylab.plot(theta_deg, numpy.sqrt(var), 'k-')
        pylab.xlabel(xlabel)
        pylab.ylabel('std-dev (m)')
        set0axis(pylab)
    
    norm = lambda x: x / x.mean()

    with r.data_pylab('report_gy_var', **figparams) as pylab:
        adjust_axes(pylab)
        for variant in variants:
            x = results[variant]['gy_var'][sick_indices]
            x /= numpy.max(abs(x))
            pylab.plot(theta_deg, numpy.sqrt(x) , label=variant)
        pylab.legend(loc='lower right')
        pylab.xlabel(xlabel)
        pylab.ylabel('norm. std-dev (unitless)')
        set0axis(pylab)

    with r.data_pylab('report_y_dot_var', **figparams) as pylab:
        adjust_axes(pylab)
        for variant in variants:
            x = results[variant]['y_dot_var'][sick_indices]
            x /= numpy.max(abs(x))
            pylab.plot(theta_deg, numpy.sqrt(x) , label=variant)
        pylab.legend(loc='lower right')
        pylab.xlabel(xlabel)
        pylab.ylabel('norm. std-dev (unitless)')
        set0axis(pylab)

    
    
    def set_x_axis(pylab):
        a = pylab.axis()
        pylab.axis([-91, +271, a[2], a[3]])
        pylab.xticks([-90, 0, 90, 180, 270])    
 
    with r.data_pylab('report_Gv', **figparams) as pylab:
        adjust_axes(pylab)
        for variant in variants:
            gy_var = results[variant]['gy_var'][sick_indices]
            x = results[variant]['G'][sick_indices, 0] / gy_var 
            #x /= normG[variant]
            x /= numpy.max(abs(x))
            pylab.plot(theta_deg, x , label=variant)
        pylab.plot(theta_deg, -sin(theta), label='expected')
        pylab.plot(theta_deg, 0 * theta, 'k--')
        #pylab.axis([0, N, -2, 2])
        #pylab.legend(loc='lower right')
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)
        set_x_axis(pylab)

    with r.data_pylab('report_Gomega', **figparams) as pylab:
        adjust_axes(pylab)
        for variant in variants:
            gy_var = results[variant]['gy_var'][sick_indices]
            x = results[variant]['G'][sick_indices, 2] / gy_var
            #x /= normG[variant]
            x /= numpy.mean(abs(x))
            pylab.plot(theta_deg, x, label=variant)
        pylab.plot(theta_deg, norm(numpy.ones((N))), label='expected')
        pylab.plot(theta_deg, 0 * theta, 'k--')
        #pylab.axis([0, N, 0, 1.5])
        pylab.legend(loc='lower right')
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)
        set_x_axis(pylab)

    with r.data_pylab('report_Bv', **figparams) as pylab:
        adjust_axes(pylab)
        for variant in variants:
            gy_var = results[variant]['gy_var'][sick_indices]
            x = results[variant]['B'][sick_indices, 0] / gy_var
            #x /= normB[variant]
            x /= numpy.max(abs(x))
            pylab.plot(theta_deg, x, label=variant)
        pylab.plot(theta_deg, -cos(theta), label='expected')
        pylab.plot(theta_deg, 0 * theta, 'k--')
        #pylab.axis([0, N, -2, 2])
        #pylab.legend(loc='lower right')
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)
        set_x_axis(pylab)

    with r.data_pylab('report_Bomega', **figparams) as pylab:
        adjust_axes(pylab)
        for variant in variants:
            gy_var = results[variant]['gy_var'][sick_indices]
            x = norm(results[variant]['B'][sick_indices, 2]) / gy_var
            # /= normB[variant]
            x /= numpy.max(abs(x)) * 10
            pylab.plot(theta_deg, x, label=variant)
        pylab.plot(theta_deg, 0 * theta, label='expected')
        #pylab.axis([0, N, -2, 2])
        #pylab.legend(loc='lower right')
        pylab.xlabel(xlabel)
        pylab.ylabel(ylabel)
        set_x_axis(pylab)

    r.figure(sub=['report_y_mean', 'report_y_var', 'report_gy_var', 'report_y_dot_var'])        
    r.figure(sub=['report_Gv', 'report_Gomega', 'report_Bv', 'report_Bomega'])        
    return r

def main():
    """
    Prepare data with:
    
        average_logs_results --dir . --experiment laser_bgds_boot
    
    """
    print "Loading first..."
    results = my_pickle_load('out/average_logs_results/laser_bgds_boot.pickle')

    report = Node('laser_bgds_boot')
    manual = my_figures(results)
    write_figures_for_paper(manual)
    report.add_child(manual)
    
    
    k = 1
    variants = sorted(results.keys())
    variants = []
    for variant in variants:
        data = results[variant] 
        G = data['G']
        B = data['B']
        
        gy_mean = data['gy_mean']
        y_mean = data['y_mean']
        one_over_y_mean = data['one_over_y_mean']
        y_dot_var = data['y_dot_var']
        y_dot_svar = data['y_dot_svar']
        gy_var = data['gy_var']
        gy_svar = data['gy_svar']
        
        print 'Considering %s' % variant
        
        n = report.node(variant)
        
        #readings = range(360, G.shape[0])
        readings = range(0, G.shape[0])
        N = len(readings)
        
        G = G[readings, :]
        B = B[readings, :]
        y_dot_var = y_dot_var[readings]
        y_dot_svar = y_dot_svar[readings]
        gy_var = gy_var[readings]
        gy_svar = gy_svar[readings] 
        
        for k in [0, 2]:
            var = 'G[%s]' % k
            G_k = n.data(var, G[:, k])
            G_k_n = G[:, k] / gy_var
            with G_k.data_pylab('original') as pylab:
                pylab.plot(G[:, k])
                pylab.title(var + ' original')
                M = abs(G[:, k]).max()
                pylab.axis([0, N, -M, M])
                           
            with G_k.data_pylab('normalized') as pylab:
                pylab.plot(G_k_n)
                pylab.title(var + ' normalized')
                M = abs(G_k_n).max()
                pylab.axis([0, N, -M, M])            

        for k in [0, 2]:
            var = 'B[%s]' % k
            B_k = n.data(var, B[:, k])
            B_k_n = B[:, k] / gy_var
            
            with B_k.data_pylab('original') as pylab:
                pylab.plot(B[:, k])
                pylab.title(var + ' original')
                M = abs(B[:, k]).max()
                pylab.axis([0, N, -M, M])            

            with B_k.data_pylab('normalized') as pylab:
                pylab.plot(B_k_n)
                pylab.title(var + ' normalized')            
                M = abs(B_k_n).max()
                pylab.axis([0, N, -M, M])            


        n.figure('obtained', sub=['B[0]/normalized', 'B[2]/normalized',
        'G[0]/normalized', 'G[2]/normalized', ])


        n.figure('G', sub=['G[0]/original', 'G[0]/normalized',
        'G[2]/original', 'G[2]/normalized'])


        n.figure('B', sub=['B[0]/original', 'B[0]/normalized',
        'B[2]/original', 'B[2]/normalized']) 
        
        
        
        theta = linspace(0, 2 * math.pi, N) - math.pi / 2
        with n.data_pylab('B_v') as pylab:
            pylab.plot(-cos(theta))
            pylab.axis([0, N, -2, 2])
        with n.data_pylab('B_omega') as pylab:
            pylab.plot(0 * theta)
            pylab.axis([0, N, -2, 2])
        with n.data_pylab('G_v') as pylab:
            pylab.plot(-sin(theta))
            pylab.axis([0, N, -2, 2])
        with n.data_pylab('G_omega') as pylab:
            pylab.plot(numpy.ones((N)))
            pylab.axis([0, N, -2, 2])
            
        n.figure('expected', sub=['B_v', 'B_omega', 'G_v', 'G_omega'])
        
        norm = lambda x: x / x.max()
        #   norm = lambda x : x
        with n.data_pylab('y_dot_var') as pylab:
            pylab.plot(norm(y_dot_var), 'b', label='y_dot_var')
            pylab.plot(norm(y_dot_svar ** 2), 'g', label='y_dot_svar')
            
            pylab.axis([0, N, 0, 1])
            pylab.legend()

        with n.data_pylab('gy_var') as pylab:
            pylab.plot(norm(gy_var) , 'b', label='gy_var')
            pylab.plot(norm(gy_svar ** 2), 'g', label='gy_svar')
            
            pylab.axis([0, N, 0, 1])
            pylab.legend()
            
            
        f = n.figure('stats')
        f.sub('y_dot_var')
        f.sub('gy_var')
        
        for var in ['y_dot_mean', 'gy_mean', 'y_mean', 'y_var', 'one_over_y_mean']:
            with n.data_pylab(var) as pylab:
                pylab.plot(data[var][readings])
            f.sub(var)
            
        with n.data_pylab('y_mean+var') as pylab:
            y = data['y_mean'][readings]
            var = data['y_var'][readings]
            pylab.errorbar(range(0, N), y, yerr=3 * numpy.sqrt(var), fmt='ro')
                
        f.sub('y_mean+var')

        print variant
        
        if True: #variant == 'GS_DS':
            s = {'variant': variant,
                 'Gl':G[:, 0] / gy_var,
                 'Ga':G[:, 2] / gy_var,
                 'Bl':B[:, 0] / gy_var,
                 'Ba':B[:, 2] / gy_var }
            filename = "out/laser_bgds_boot/%s:GB.pickle" % variant.replace('/', '_')
            make_sure_dir_exists(filename)
            my_pickle_dump(s, filename)
            print 'Written on %s' % filename
        

    node_to_html_document(report, 'out/laser_bgds_boot/report.html')

if __name__ == '__main__':
    main()
    
def write_figures_for_paper(report):
    output_conf = 'out/laser_bgds_boot/figures/conf.tex'
    output_rep = 'out/laser_bgds_boot/figures/report.tex'
    graphics_path = 'out/laser_bgds_boot/figures/'
    summary = 'out/laser_bgds_boot/figures/summary.tex'
    
    if not os.path.exists(graphics_path):
        os.makedirs(graphics_path)
        
    with Latex.document(summary, document_class='ieeeconf',
                        graphics_path=graphics_path) as doc:
        doc.input('conf')

    write_figures_for_paper_(output_conf, report, graphics_path, True)
    write_figures_for_paper_(output_rep, report, graphics_path, False)
    

def write_figures_for_paper_(frag_file, report, graphics_path, conference):
    if conference:
        w1 = "4cm" 
    else:
        w1 = "5.5cm"
    
    with Latex.fragment(frag_file, graphics_path=graphics_path) as frag:
        with frag.figure(caption=makecmd(frag, 'LaserStatsCaption'),
                         label=makelabel('LaserStats'), double=True) as fig:
            fig.hfill()
            with fig.subfigure(caption=makecmd(frag, 'report_y_mean')) as sub:
                data = report.resolve_url('report_y_mean')
                write_graphics(sub, data, w1, border=False)
            fig.hfill()
            with fig.subfigure(caption=makecmd(frag, 'report_y_var')) as sub:
                data = report.resolve_url('report_y_var')
                write_graphics(sub, data, w1, border=False)
            fig.hfill()
            
            if not conference:
                fig.parbreak()
                fig.hfill()
            
            with fig.subfigure(caption=makecmd(frag, 'report_gy_var')) as sub:
                data = report.resolve_url('report_gy_var')
                write_graphics(sub, data, w1, border=False)
            fig.hfill()
            with fig.subfigure(caption=makecmd(frag, 'report_y_dot_var')) as sub:
                data = report.resolve_url('report_y_dot_var')
                write_graphics(sub, data, w1, border=False)
            fig.hfill() 
            
        with frag.figure(caption=makecmd(frag, 'LaserTensorsCaption'),
                         label=makelabel('LaserTensors'), double=True) as fig:
            fig.hfill()
            with fig.subfigure(caption=makecmd(frag, 'report_Gv')) as sub:
                data = report.resolve_url('report_Gv')
                write_graphics(sub, data, w1, border=False)
            fig.hfill()
            with fig.subfigure(caption=makecmd(frag, 'report_Gomega')) as sub:
                data = report.resolve_url('report_Gomega')
                write_graphics(sub, data, w1, border=False)
            fig.hfill()
            
            if not conference:
                fig.parbreak()
                fig.hfill()
            
            with fig.subfigure(caption=makecmd(frag, 'report_Bv')) as sub:
                data = report.resolve_url('report_Bv')
                write_graphics(sub, data, w1, border=False)
            fig.hfill()
            with fig.subfigure(caption=makecmd(frag, 'report_Bomega')) as sub:
                data = report.resolve_url('report_Bomega')
                write_graphics(sub, data, w1, border=False)
            fig.hfill() 
