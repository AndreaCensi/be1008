import cPickle as pickle
import numpy
from numpy import nonzero, array, abs


from reprep.node import Node
from reprep.out.html import node_to_html_document

def laser_bgds_boot_display():
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
        
        y_dot_var = data['y_dot_var']
        y_dot_svar = data['y_dot_svar']
        gy_var = data['gy_var']
        gy_svar = data['gy_svar']
        
        print 'Considering %s' % variant
        
        n = report.node(variant)
        
        #readings = range(0, 300)
        readings = range(360, G.shape[0])
        N = len(readings)
        G = G[readings, :]
        B = B[readings, :]
        y_dot_var = y_dot_var[readings]
        y_dot_svar = y_dot_svar[readings]
        gy_var = gy_var[readings]
        gy_svar = gy_svar[readings]
        
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


        fG = n.figure('G')
        fG.sub('G[0]/original')
        fG.sub('G[0]/normalized')
        fG.sub('G[2]/original')
        fG.sub('G[2]/normalized')

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

        
        
        fB = n.figure('B')
        fB.sub('B[0]/original')
        fB.sub('B[0]/normalized')
        fB.sub('B[2]/original')
        fB.sub('B[2]/normalized')

    node_to_html_document(report, 'laser_bgds_boot.html')

if __name__ == '__main__':
    laser_bgds_boot_display()
