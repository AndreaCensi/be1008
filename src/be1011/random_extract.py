import numpy, numpy.random
from procgraph import Block, BadInput

class RandomExtract(Block):
    ''' This block extracts randomly some of the sensels from the stream.
    
        It can accept multiple streams, but they must have all the same size.
     '''
    
    Block.alias('random_extract')
    
    Block.input_is_variable()
    Block.output_is_variable()
    
    Block.config('n', 'Number of sensels to extract.')
    
    def init(self):
        self.selection = None
        
    def update(self):
        
        for i in range(self.num_input_signals()):
            x = self.get_input(i)
            if x is None:
                continue
        
            if self.selection is None:
                self.signal_shape = x.shape
                self.selection = \
                    RandomExtract.choose_selection(k=self.config.n, n=x.size)
            else:
                if self.signal_shape != x.shape:
                    raise BadInput('Signals have different shape.', self, i)
                
            # I'm not sure why x.flat fails
            selected = x.flat[self.selection]
            
            self.set_output(i, selected)
        
    @staticmethod
    def choose_selection(k, n):
        ''' Select k indices from n. '''
        # a simple but expensive way to do it
        r = numpy.random.rand(n)
        index_array = numpy.argsort(r)
        return index_array[0:k]
        
        