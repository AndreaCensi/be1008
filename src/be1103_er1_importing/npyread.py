from procgraph import Block, BadConfig, Generator
import os
import numpy

def memory_map_file(filename):
    """ 
        Returns a memory-mapped numpy array. 
        A file called filename + .dtype should exist 
    """
    dtype = numpy.dtype(eval(open(filename + ".dtype").read()))

    file_length = os.path.getsize(filename)
    record_length = dtype.itemsize
    num_available = file_length / record_length
    if num_available * record_length != file_length:
        msg = ("Warning: file %r has fractionary size. File: %d Record: %d"
              "Num: %d Num*record: %d" % (filename,
              file_length, record_length,
              num_available, num_available * record_length))
        print(msg)
    
    a = numpy.memmap(filename, dtype=dtype, mode='r', shape=(num_available,))
    
    return a

class NPYRead(Generator):
    ''' Reads a .npy file with corresponding .npy.dtype dtype hint. '''
    Block.alias('npyread')
    
    Block.config('file',
                 '``.npy`` file to read. A ``XXX.npy.dtype`` file must exist as well')
    
    Block.output('value')
    
    def init(self):
        dtype_file = self.config.file + '.dtype'
        
        if not os.path.exists(self.config.file):
            msg = 'File %r does not exist.' % self.config.file
            raise BadConfig(msg, self, 'file')
        
        if not os.path.exists(dtype_file):
            msg = 'File %r does not exist.' % dtype_file
            raise BadConfig(msg, self, 'file')

        self.info('Reading from %r.' % self.config.file)
        self.array = memory_map_file(self.config.file)
        
        self.counter = 0
        self.timestamp = self.array[0]['timestamp']
        fields = list(self.array.dtype.fields)
        fields.remove('timestamp')
        field = fields[0]
        self.value = self.array[field]
        self.nsamples = len(self.value) 
        self.timestamp = self.array['timestamp']
        self.counter = 0
        self.next_value = self.value[self.counter]
        self.next_timestamp = self.timestamp[self.counter]

        self.debug('Shape: {0!r}'.format(self.array.shape))
        self.debug('Dtype: {0!r}'.format(self.array.dtype))
        self.debug('    #: %d' % self.nsamples)
        t0 = self.timestamp[0]
        t1 = self.timestamp[self.nsamples - 1]
        self.debug(' duration: %.1f seconds' % (t1 - t0))
        
    def update(self):
        self.set_output(0, self.next_value, timestamp=self.next_timestamp)
        self.counter += 1
        if self.counter < len(self.value):
            self.next_value = self.value[self.counter]
            self.next_timestamp = self.timestamp[self.counter]
        else:
            self.next_timestamp = None
            
    def next_data_status(self):
        # TODO: put new interface
        if self.next_timestamp is None: # EOF
            return (False, None)
        else:
            return (True, self.next_timestamp)

    def finish(self):
        del self.array