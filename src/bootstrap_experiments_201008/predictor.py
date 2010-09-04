from procgraph import Block 

import cPickle as pickle
from numpy import sign
from procgraph.components.basic import  register_simple_block
import numpy

register_simple_block(lambda x: 1.0 / x, 'one_over')

def count_less_than_zero(values):
    ''' Returns the fraction of zero elements in the array. '''
    ok = (values <= 0).mean()
    return ok

register_simple_block(count_less_than_zero)


class BGDSPredictor(Block):
    
    Block.alias('bgds_predictor')
    
    Block.config('G', 'Data produced by camera_bgds_boot_display')
    Block.input('gx', 'Gradient of image along direction x.')
    Block.input('gy', 'Gradient of image along direction y.')
    Block.input('y_dot', 'Derivative of y.')
    Block.input('commands', 'Commands (``[vx,vy,omega]``).')
    
    Block.output('y_dot_pred', 'Predicted y_dot')
    Block.output('error', 'Disagreement between actual and predicted y_dot.')
    
    def init(self):
        # XXX not compatible with saving procedure
        
        filename = self.config.G
        
        self.G = pickle.load(open(filename, 'rb')) 
        
        self.define_input_signals(['gx', 'gy', 'y_dot', 'commands'])
        self.define_output_signals(['y_dot_pred', 'error'])
        
    def update(self):
        gx = self.input.gx
        gy = self.input.gy
        y_dot = self.input.y_dot
        commands = self.input.commands
        Gxl = self.G['Gxl']
        Gyl = self.G['Gyl']
        Gxa = self.G['Gxa']
        Gya = self.G['Gya']
        lvel = commands[0]
        avel = commands[2]
        
        y_dot_pred = \
            lvel * Gxl * gx + \
            lvel * Gyl * gy + \
            avel * Gxa * gx + \
            avel * Gya * gy;  
        
        self.output.y_dot_pred = y_dot_pred
        #self.output.error = numpy.maximum(0, -y_dot_pred * y_dot)
        self.output.error = (abs(sign(y_dot_pred) - sign(y_dot))) 
        #* (abs(y_dot) + abs(y_dot_pred)) 
         
