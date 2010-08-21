import pickle
from reprep.node import Node
from reprep.out.html import node_to_html_document
import numpy

def camera_bgds_boot_display():
    results = pickle.load(open('camera_bgds_boot.pickle', 'rb'))
    
    
    report = Node('camera_bgds_boot') 
    
    k = 1
    for variant, data in results.items():
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
        
        
        k += 1
        if k > 2:
            pass
            # break
    
    node_to_html_document(report, 'camera_bgds_boot.html')

if __name__ == '__main__':
    camera_bgds_boot_display()
