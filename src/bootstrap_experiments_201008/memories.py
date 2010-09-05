
from procgraph import Block
from procgraph.core.model_loadsave import make_sure_dir_exists
import pickle

class Memories(Block):
    Block.alias('memories')
    
    Block.config('logdir', 'Rawseeds log')
    
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
            'Bicocca_2009-02-25a' : [0, 0.1, 0.2, 2, 2.5, 5, 5.7, 9, 9.5]
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
        data = {'logdir':self.config.logdir, 'instant': instant,
                'time':self.time, 'timestamp': self.get_input_timestamp(0) }
        for name in self.get_input_signals_names():
            data[name] = self.get_input(name)
        filename = "out/memories/{log}/{time}.pickle".format(
                    log=self.config.logdir, time=instant)
        make_sure_dir_exists(filename)
        pickle.dump(data, open(filename, 'w'))
             
             
             
             
             
