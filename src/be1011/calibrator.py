import numpy

from procgraph import Block
from be1011.random_extract import RandomExtract

#   1) choose random pixels as reference points
#   2) plot these on the output
#   3) also output M
#   3) convert correctly:
#      a) normalize correlation (cov2corr)
#      b) D = arc cos???? 


class Calibrator(Block):
    ''' 
    Needs synchronized y, y_dot.
    '''
    Block.alias('calibrator')

    Block.config('num_ref', 'Number of reference points.', 50)
    
    Block.config('interval', 'Interval for computing stats.', 5)
    Block.input('y')
    Block.input('y_dot')
    
    Block.output('eigenvalues')
    Block.output('corr')
    Block.output('M', 'Computed covariance')
    
    Block.output('x_y', 'tuple (x,y) of guessed coordinates')
    Block.output('x', 'Coordinates')
    Block.output('y', 'Coordinates')
    Block.output('z', 'Coordinates')
    Block.output('variance')
    Block.output('correlation')
    
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
            y = y.flatten()
            y_dot = y_dot.flatten()
        
        assert y.ndim == y_dot.ndim == 1
        
        n = self.num_samples
        
        k = int(self.config.num_ref)
        
        if self.M is None:
            self.M = numpy.zeros(shape=(k, y.size), dtype='float32')
            self.variance = numpy.zeros(shape=(y.size,), dtype='float32')
            #self.output.eigenvalues = numpy.zeros(k)
            self.refs = RandomExtract.choose_selection(k, y.size)
            
        for i in range(k):
            d = y_dot[ self.refs[i] ] * y_dot
            self.M[i, :] = (n * self.M[i, :] + d) / float(n + 1)
            
        variance_up = y_dot * y_dot
        self.variance[:] = (n * self.variance + variance_up) / float(n + 1)
        
        if n % self.config.interval == 0:
            try:
                self.write_output()
            except numpy.linalg.linalg.LinAlgError as e:
                self.error(e)
            
        self.num_samples += 1
    
    def write_output(self):
        k = int(self.config.num_ref)
        
        #print '%f %f' % (self.M.max(), self.M.min())
        
        # normalize correlation
        correlation = self.M.copy()
        variance_safe = self.variance.copy()
        problematic = variance_safe == 0
        #print "num problematic: %d " % (len(numpy.nonzero(problematic)[0]))
        variance_safe[problematic] = 1
        one_over_std = 1 / numpy.sqrt(variance_safe)
        for i in range(k):
            one_over_std_i = one_over_std[self.refs[i]]
            correlation[i, :] = (correlation[i, :] * one_over_std_i) * one_over_std
            #print '%d %f %f' % (i, correlation[i, :].max(), correlation[i, :].min())
            
        #print '%f %f' % (correlation.max(), correlation.min())
        
        assert numpy.isfinite(correlation).all()
        assert (correlation <= +1.0001).all()
        assert (correlation >= -1.0001).all()
        # fix numerical errors
        correlation = numpy.minimum(correlation, +1.0)
        correlation = numpy.maximum(correlation, -1.0)
        
        # create distances from correlation
        # correlation = 1 -> distance of 0
        # correlation /= numpy.abs(correlation).max()
        #D = numpy.arccos(correlation)
        D = correlation
        assert numpy.isfinite(D).all()
        assert numpy.isreal(D).all()
        
        U, S, V = numpy.linalg.svd(D, full_matrices=0) #@UnusedVariable
        assert S.size == k
        self.output.eigenvalues = S[0:] / S[0]
        
        self.x = V[0, :] * numpy.sqrt(S[0])
        self.y = V[1, :] * numpy.sqrt(S[1])
        self.z = V[2, :] * numpy.sqrt(S[2])
        
        self.x /= numpy.abs(self.x).max()
        self.y /= numpy.abs(self.y).max()
        self.z /= numpy.abs(self.z).max()
        
        
        self.output.x_y = (self.y, self.z)
        self.output.x = self.x
        self.output.y = self.y
        self.output.z = self.z
        
        i = 0
        d = self.M[i, :].copy()
        d[ self.refs[i] ] = numpy.nan 
        self.output.corr = d
        
        self.output.M = self.M.copy()
        self.output.variance = self.variance
        self.output.correlation = correlation
        
