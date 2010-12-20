import numpy
import cPickle as pickle
from bisect import bisect_left

from procgraph import Block


class PopulationCode(Block):
    ''' Converts the input into a population code. '''
    
    Block.alias('popcode')
    
    # Block.input('edges', 'Array specifying the population boundaries.')
    Block.config('edges', 'Pickle file containing the array specifying the '
                          'population boundaries.')
    
    Block.input('x', 'Values to convert')
    
    Block.output('pop')
    
    def init(self):
        self.edges = numpy.array(pickle.load(open(self.config.edges, 'rb')))        
    
        self.info('Using edges: %s' % self.edges)
    
    def update(self):
        self.output[0] = population_code(self.edges, self.input[0])


def population_code(edges, x):
    ncells = edges.size - 1
    nsensels = x.size
    result = numpy.zeros((nsensels, ncells), dtype='float32')
    for i in range(nsensels):
        result[i, :] = population_code_single(edges, x[i])
    return result.T

def population_code_single(edges, x):
    if x < edges[0]:
        x = edges[0]
    if x > edges[-1]: 
        x = edges[-1]
    
    ncells = edges.size - 1
    result = numpy.zeros((ncells,), dtype='float32')

    i = bisect_left(edges, x) - 1
    if i < 0:
        i = 0
    if i >= ncells - 1:
        i = ncells - 1
        
    assert edges[i] <= x <= edges[i + 1]
    
    tau = (x - edges[i]) / (edges[i + 1] - edges[i])
    
    result[i] = 1 - tau
    
    if i < ncells - 1:
        result[i + 1] = tau

    return result
    
    
        
