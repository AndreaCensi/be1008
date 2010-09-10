import os
import cPickle as pickle
from bz2 import BZ2File

def my_pickle_dump(obj, filename):
    '''
        Filename can be only the basename, we append .pickle.bz2 if necessary.
        
    '''
    print 'Writing to %s' % filename
    
    dir = os.path.dirname(filename)
    if not os.path.exists(dir):
        os.makedirs(dir)
        
    if not filename.endswith('.pickle'):
        filename = filename + '.pickle'
        f = open(filename, 'wb')
    
    if not filename.endswith('.bz2'):
        f = BZ2File(filename + '.bz2', 'wb')
        
    pickle.dump(obj, f)

def my_pickle_load(filename):
    
    print 'Reading from %s' % filename
    
    bzf = filename + '.bz2'
    
    if filename.endswith('.bz2'):
        f = BZ2File(filename, 'rb')
    elif os.path.exists(bzf):
        f = BZ2File(bzf, 'rb')
    else:
        f = open(filename, 'rb')
        
    return pickle.load(f)    
    
