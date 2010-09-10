
from procgraph import Block
from procgraph.core.model_loadsave import make_sure_dir_exists
import pickle
from be1008.utils import my_pickle_dump

class Memories(Block):
    Block.alias('memories')
    
    Block.config('other', 'additional hash to save')
    Block.config('prefix', 'subdirectory')
    Block.config('logdir', 'chooses which one')
    
    Block.input_is_variable()
    
    def init(self):
        self.define_output_signals([])
        
        self.info('Considering memories for {logdir}'.format(logdir=self.config.logdir))
        self.state.done = []
        self.state.first_timestamp = None
        
    def update(self):
        if self.state.first_timestamp is None:
            self.state.first_timestamp = self.get_input_timestamp(0)
            
        self.time = self.get_input_timestamp(0) - self.state.first_timestamp
        
        interesting = {
            'Bicocca_2009-02-25a' : [0, 0.1, 0.2, 2, 2.5, 5, 5.7, 9, 9.5],
            'Bicocca_2009-02-26a' : [3, 4, 18, 19, 20, 45, 46, 47, 48, 49, 50,
                                     75, 76, 77, 78, 79, 80, 99, 100, 101, 102,
                                     120, 121, 122, 123, 124, 125, 126, 127,
                                     139, 140, 141],
            'Bovisa_2008-10-06': [23, 24, 25, 26, 27, 28],
            'Bovisa_2008-10-07': [13, 14, 15, 37],
        } 

        if not self.config.logdir in interesting:
            return
        
        
        moments = interesting[self.config.logdir] 
        
        for m in moments:
            if self.time > m and not (m in self.state.done):
                self.info('Making snapshot for time {0}'.format(m))
                self.make_snapshot(m)
                
                self.state.done.append(m)
             
    def make_snapshot(self, instant):
        data = { 'instant': instant,
                'time':self.time, 'timestamp': self.get_input_timestamp(0),
                'prefix':self.config.prefix }
        
        data.update(**self.config.other)
        
        for name in self.get_input_signals_names():
            data[name] = self.get_input(name)
        filename = "{prefix}/{time:.2f}.pickle".format(
                    time=instant,
                    prefix=self.config.prefix)
        make_sure_dir_exists(filename)
        my_pickle_dump(data, filename)

             
             
             
             
             
