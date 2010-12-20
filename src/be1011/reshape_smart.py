import numpy

from procgraph import COMPULSORY
from procgraph.core.registrar_other import simple_block

# TODO: case width = None -> sqrt
# TODO: resize 2D
@simple_block
def reshape_smart(x, width=COMPULSORY):
    ''' Reshapes x into (?, width) if x is 1D.
    
        If x is 2D, it is left alone.
    '''
    
    if x.ndim == 2:
        return x
    
    n = len(x.flat)
    height = numpy.ceil(n * 1.0 / width)
    
    #print("sha: %s  n: %d  with: %d  height: %d" % (x.shape,n,width,height))
    
    y = numpy.zeros(shape=(height, width), dtype=x.dtype)
    y.flat[0:n] = x
    
    return y 
