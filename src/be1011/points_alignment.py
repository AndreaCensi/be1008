import numpy as np
from contracts import contracts, check
from snp_geometry.random_geometry import geodesic_distance_on_S2

@contracts(X='array[3xN]', Y='array[3xN]', returns='array[3x3],orthogonal')
def find_best_orthogonal_transform(X, Y):
    ''' Finds the best orthogonal transform R (R in O(3)) between X and Y,
        such that R X ~= Y. '''
    YX = np.dot(Y, X.T)
    check('array[3x3]', YX)
    U, S, V = np.linalg.svd(YX) #@UnusedVariable
    best = np.dot(U, V)
    return best
    
@contracts(X='array[3xN]', Y='array[3xN]', returns='float,>=0')
def overlap_error_after_orthogonal_transform(X, Y):
    ''' Computes the norm of the residual after X and Y (vectors of direction)
        are optimally rotated/mirrored to best overlap with each other. 
        The result is returned in average degrees.
    '''
    O = find_best_orthogonal_transform(X, Y)
    X2 = np.dot(O, X)
    N = X.shape[1]
    average_error = 0
    for i in range(N):
        average_error += geodesic_distance_on_S2(X2[:, i], Y[:, i])
    average_error /= N
    return average_error
    
    
