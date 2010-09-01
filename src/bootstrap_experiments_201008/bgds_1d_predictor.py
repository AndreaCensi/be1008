from procgraph import Block, block_alias, block_config, block_input, block_output 

import cPickle as pickle
from numpy import sign



class BGDS1dPredictor(Block):
    block_alias('bgds_1d_predictor')
    
    block_config('BG', 'pickle file produced by ``laser_bgds_boot_disp``.')
    
    block_input('gy', 'Gradient of y.')
    block_input('y_dot', 'Derivative of y.')
    block_input('commands', 'Commands (``[vx,vy,omega]``).')
    
    block_output('y_dot_pred', 'Predicted y_dot')
    block_output('error', 'Disagreement between actual and predicted y_dot.')
    
    def init(self):
        # XXX not compatible with saving procedure
        
        filename = self.config.BG
        
        self.BG = pickle.load(open(filename, 'rb')) 
        
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
        self.output.error = (abs(sign(y_dot_pred) - sign(y_dot))) * (abs(y_dot) + abs(y_dot_pred)) 
        
 
