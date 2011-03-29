import numpy
import cPickle as pickle

from procgraph import Block, BadConfig
from contracts import check, check_multiple

from .generic_bgds_boot import check_inputs_synchronized,generalized_gradient

class GenericPredictor(Block):
    Block.alias('generic_bgds_predict')
    
    Block.input('y')
    Block.input('y_dot')
    Block.input('u')
    
    Block.config('tensors')
    
    Block.output('y_dot_pred')
    Block.output('error')
    Block.output('error_stats')
    
    Block.output('error_sensel', 'Sum of the disagreement for each sensel.')
    
    def init(self):
        try:
            with open(self.config.tensors, 'rb') as f:
                tensors = pickle.load(f)
        except Exception as e:
            raise BadConfig("%s" % e, self, 'file')

        self.T = tensors['Gnn']
        check('array,(array[Kx2xHxW]|array[Kx1xN])', self.T)
        
    def update(self):
        check_inputs_synchronized(self)
        
        y_dot = self.input.y_dot
        y = self.input.y
        u = self.input.u
        T = self.T
        
        check_multiple([
            ('shape(x),(array[HxW]|array[N])', y),
            ('shape(x),(array[HxW]|array[N])', y_dot),
            ('array[K]', u),
            ('array[Kx2xHxW]|array[Kx1xN]', T), # TODO: use references
        ])
        K = u.size
        
        # update covariance of gradients
        gy = generalized_gradient(y)
        
        Tgy = np.tensordot([1, 1], T * gy , axes=(0, 1)) 
                
        y_dot_pred = np.tensordot(u, Tgy, axes=(0, 0))
         
        assert y_dot_pred.ndim == 2
        
        error = np.maximum(0, -y_dot_pred * y_dot)
        # error = np.abs(np.sign(y_dot_pred) - np.sign(y_dot))
        
        self.output.y_dot_pred = y_dot_pred
        self.output.error = error
        self.output.error_sensel = np.sum(error, axis=0)
        
        
        

        
