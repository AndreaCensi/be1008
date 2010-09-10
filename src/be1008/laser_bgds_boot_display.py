import cPickle as pickle
import numpy
from numpy import nonzero, array, abs


from reprep.node import Node
from reprep.out.html import node_to_html_document
from numpy.lib.function_base import linspace
import math
from numpy.ma.core import cos, sin
from procgraph.core.model_loadsave import make_sure_dir_exists

def main():
    """
    Prepare data with:
    
        average_logs_results --dir . --experiment laser_bgds_boot
    
    """
    print "Loading first..."
    results = pickle.load(open('laser_bgds_boot.pickle', 'rb'))

    report = Node('laser_bgds_boot') 
    
    k = 1
    variants = sorted(results.keys())
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
            pickle.dump(s, open(filename, 'wb'))
            print 'Written on %s' % filename
        

    node_to_html_document(report, 'out/laser_bgds_boot.html')

if __name__ == '__main__':
    laser_bgds_boot_display()
