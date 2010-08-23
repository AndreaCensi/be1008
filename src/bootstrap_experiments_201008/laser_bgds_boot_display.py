import cPickle as pickle
import numpy
from numpy import nonzero, array, abs
from matplotlib import pylab

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
        
        print 'Considering %s' % variant
        
        n = report.node(variant)
        
        #readings = range(0, 300)
        
        G = G[360:, :]
        B = B[360:, :]
        
        for k in [0, 2]:
            G_k = n.data('G[%s]' % k, G[:, k])
            with G_k.data_file('plot', 'image/png') as filename:
                pylab.figure()
                pylab.plot(G[:, k])
                
                m = abs(G[:, k]).max()
                a = array(pylab.axis())
                a[2] = -m
                a[3] = +m
                pylab.axis(a)
                
                pylab.savefig(filename)
                pylab.close() 
        
        for k in [0, 2]:
            B_k = n.data('B[%s]' % k, B[:, k])
            with B_k.data_file('plot', 'image/png') as filename:
                pylab.figure()
                pylab.plot(B[:, k])
                
                m = abs(B[:, k]).max()
                a = array(pylab.axis())
                a[2] = -m
                a[3] = +m
                pylab.axis(a)
                
                pylab.savefig(filename)
                pylab.close() 
        
        
        fG = n.figure('G')
        fG.sub('G[0]')
        fG.sub('G[2]')
        fB = n.figure('B')
        fB.sub('B[0]')
        fB.sub('B[2]')

    node_to_html_document(report, 'laser_bgds_boot.html')

if __name__ == '__main__':
    laser_bgds_boot_display()
