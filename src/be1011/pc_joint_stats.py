import numpy
from numpy import multiply

from procgraph import Block 

class PCHistogram(Block):
    ''' Given the output of the popcode block, 
        computes the histograms for each couple of variables. '''
    Block.alias('pc_joint_stats')
    
    Block.input('pc', 'A KxN array, interpreted as population code for N variables '
                      'with K bins for each variable.')
    Block.output('joint', 'An NxNxKxK array, containing the joint distribution.')
    Block.output('single', 'A NxK array, containing the single distribution of each '
                            'variable.')
    
    def init(self):
        self.joint = None
        self.single = None
        
    def update(self):
#        pc = (self.input.pc * 10).astype('int16')
        pc = numpy.ceil(self.input.pc).astype('uint8')
        K, N = pc.shape 
        if self.joint is None:
            self.joint = numpy.zeros(shape=(N, N, K, K), dtype='uint16')
            self.single = numpy.zeros(shape=(N, K), dtype='uint16')
        
        self.single += pc.T
        
        # x = K x N x K x N
        x = multiply.outer(pc, pc)
        y = numpy.transpose(x, (1, 3, 0, 2))
        
        self.joint += y
        
        print self.joint.max(), self.single.max()
        
        self.output.single = self.single
        self.output.joint = self.joint
        
