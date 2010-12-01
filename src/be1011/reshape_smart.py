import numpy


def reshape_smart(x, width):
    n = len(x.flat)
    height = numpy.ceil(n * 1.0/ width)
    
    #print("sha: %s  n: %d  with: %d  height: %d" % (x.shape,n,width,height))
    
    y = numpy.zeros(shape=(height, width), dtype=x.dtype)
    y.flat[0:n] = x
    
    return y 
    
    
from procgraph.components.basic import COMPULSORY, register_simple_block
register_simple_block(reshape_smart, params={'width': COMPULSORY})