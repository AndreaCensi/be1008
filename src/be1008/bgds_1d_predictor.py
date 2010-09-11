import cPickle as pickle
from numpy import sign

from procgraph import Block
from be1008.utils import my_pickle_load

class BGDS1dPredictor(Block):
    Block.alias('bgds_1d_predictor')
    
    Block.config('BG', 'pickle file produced by ``laser_bgds_boot_disp``.')
    
    Block.input('gy', 'Gradient of y.')
    Block.input('y_dot', 'Derivative of y.')
    Block.input('commands', 'Commands (``[vx,vy,omega]``).')
    
    Block.output('y_dot_pred', 'Predicted y_dot')
    Block.output('error', 'Disagreement between actual and predicted y_dot.')
    
    def init(self):
        # XXX not compatible with saving procedure
    
        self.BG = my_pickle_load(self.config.BG) 
        
        self.define_input_signals(['gy', 'y_dot', 'commands'])
        self.define_output_signals(['y_dot_pred', 'error'])
        
    def update(self):
        gy = self.input.gy
        y_dot = self.input.y_dot
        commands = self.input.commands
        Gl = self.BG['Gl']
        Ga = self.BG['Ga']
        Bl = self.BG['Bl']
        Ba = self.BG['Ba']
        lvel = commands[0]
        avel = commands[2]
        
        y_dot_pred = \
            lvel * Gl * gy + \
            avel * Ga * gy + \
            lvel * Bl + \
            avel * Ba ;  
        
        self.output.y_dot_pred = y_dot_pred
        #self.output.error = numpy.maximum(0, -y_dot_pred * y_dot)
        self.output.error = abs(sign(y_dot_pred) - sign(y_dot))
        #self.output.error =         (abs(sign(y_dot_pred) - sign(y_dot))) * (abs(y_dot) + abs(y_dot_pred)) 
        
 
