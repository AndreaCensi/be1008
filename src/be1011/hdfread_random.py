from procgraph  import Block, Generator
from procgraph_hdf.hdfread import HDFread
import numpy


class HDFreadRandom(HDFread):
    ''' This block reads the long in a random fashion.
    '''
    
    Block.alias('hdfread_random')
    Block.output_is_defined_at_runtime()
    Block.config('file', 'HDF file to write')
    Block.config('signals', 'Which signals to output (and in what order). '
                 'Should be a comma-separated list. '
                 'If you do not specify it will be all signal in the original order',
                 default=None)

        
    def init(self):
        HDFread.init(self)
        
        lengths = [len(table) for table in self.signal2table.values()]
        if not len(numpy.unique(lengths)) == 1:
            raise Exception('I want a log whose lengths are the same, not %r.' 
                            % lengths)
        
        self.sequence = numpy.random.permutation(lengths[0])
        self.sequence_index = 0
        
    def update(self):
        index = self.sequence[self.sequence_index]
        self.info('Index: %d  corresponds to %d.' % (self.sequence_index, index))
        for signal, table in self.signal2table.items():
            value = table[index]['value']
            self.set_output(signal, value, self.sequence_index)
        self.sequence_index += 1

    def next_data_status(self): 
        if self.sequence_index >= len(self.sequence):
            return (False, None)
        
        # XXX: would it work if the log was empty?
        
        ts = self.sequence_index
        
        return (True, ts) 
                
        
        
        
        
        
        
