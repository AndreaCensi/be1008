import numpy
import itertools

from procgraph import Block, BadInput
 
from procgraph_numpy_ops.filters import outer
from procgraph_numpy_ops.gradient1d import gradient1d
from procgraph_cv.opencv_utils import gradient

def check_inputs_synchronized(block):
    for s in block.get_input_signals_names():
        if block.get_input(s) is None:
            raise BadInput("Signals not properly synchronized.", self, s)
    
class GenericBGDSBoot(Block):
    Block.alias('generic_bgds_boot')
    
    Block.input('y')
    Block.input('y_dot')
    Block.input('u')
    
    Block.output('G')
    Block.output('P')
    Block.output('Q')
    
    def init(self):
        self.G = None
    
    def update(self):
        check_inputs_synchronized(self)
        
        y_dot = self.input.y_dot.astype('float32')
        y = self.input.y.astype('float32')
        u = self.input.u.astype('float32')
        
        if self.G is None:
            self.init_structures(y, u)
        
        # Coefficients for updating expectations    
        alpha = self.num_samples / (self.num_samples + 1.0)
        beta = 1.0 / (self.num_samples + 1.0)
        
        # update covariance of u
        self.Q = alpha * self.Q + beta * outer(u, u)
        
        # update covariance of gradients
        gy = generalized_gradient(y)
        # the gradient has dimensions:
        #  (ndim) + gy.shape 
        self.P = alpha * self.P + beta * outer_first_dim(gy)
        
        # Finally, update G
        # M = (K x ndim x H x W )
        Gi = outer(u, gy * y_dot)
        self.G = alpha * self.G + beta * Gi

        #self.output.trP = numpy.trace(self.P) # trace over first two dimensions        
        self.output.G = self.G
        self.output.P = self.P
        self.output.Q = self.Q
        
        self.num_samples += 1
        
    def init_structures(self, y, u):
        if not y.ndim in [1, 2]:
            raise BadInput('I expect a 1D or 2D signal for y.', self, 'y')
        if u.ndim != 1:
            raise BadInput('I expect a 1D signal for u.', self, 'u')
        
        # Dimensions of G:
        # - for 1D signals:
        #     (K x ndim x N )
        # - for 2D:
        #     (K x ndim x H x W )
        shape = (u.size, y.ndim) + y.shape
        self.G = numpy.zeros(shape=shape, dtype='float32')

        # Covariance of gradient
        #    (ndim x ndim x H x W )
        shape = (y.ndim, y.ndim) + y.shape
        self.P = numpy.zeros(shape=shape, dtype='float32') 
        
        # Covariance of input
        shape = (u.size, u.size) 
        self.Q = numpy.zeros(shape=shape, dtype='float32') 
        
        self.num_samples = 0
        
def generalized_gradient(y):
    assert y.ndim in [1, 2]
    shape = (y.ndim,) + y.shape
    gy = numpy.zeros(shape, 'float32')
    if y.ndim == 1:
        gy[0, ...] = gradient1d(y)
    else:
        x, y = gradient(y) 
        gy[0, ...] = x
        gy[1, ...] = y
    return gy
        
def outer_first_dim(x):
    K = x.shape[0]
    result_shape = (K,) + x.shape
    result = numpy.zeros(shape=result_shape, dtype='float32')
    for (i, j) in itertools.product(range(K), range(K)):
        result[i, j, ...] = x[i, ...] * x[j, ...]
    return result

        
        
    
