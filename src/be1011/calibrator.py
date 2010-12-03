import numpy

from procgraph import Block, BadInput

class Calibrator(Block):
    ''' 
    Needs synchronized y, y_dot.
    '''
    Block.alias('calibrator')

    Block.config('num_ref', 'Number of reference points.', 100)
    
    Block.config('interval', 'Interval for computing stats.', 5)
    Block.input('y')
    Block.input('y_dot')
    
    Block.output('eigenvalues')
    Block.output('x_y', 'tuple (x,y) of guessed coordinates')
    
    def init(self):
        self.M = None
        self.num_samples = 0
        
    def update(self):
        # TODO: check_all_inputs_ok(self)
        y = self.input.y
        y_dot = self.input.y_dot
        assert y is not None and y_dot is not None 
        assert y.shape == y_dot.shape
        if y.ndim > 1:
            raise BadInput('I can accept 1D input, not shape %r.' % str(y.shape),
                           self, 'y')
        
        n = self.num_samples
        k = int(self.config.num_ref)
        
        if self.M is None:
            self.M = numpy.zeros(shape=(k, y.size), dtype='float32')
            self.output.eigenvalues = numpy.zeros(k)
            
        for i in range(k):
            d = y_dot[i] * y_dot
            update = (n * self.M[i, :] + d) / float(n + 1)
            self.M[i, :] = update
            
        if n % self.config.interval == 0:
            U, S, V = numpy.linalg.svd(self.M, full_matrices=0)
            assert S.size == k
            self.output.eigenvalues = S / S[0]
            
            self.x = V[0, :] * numpy.sqrt(S[0])
            self.y = V[1, :] * numpy.sqrt(S[1])
            
            self.x /= numpy.abs(self.x).max()
            self.y /= numpy.abs(self.y).max()
            
            self.output.x_y = (self.x, self.y)
         
        self.num_samples += 1
        