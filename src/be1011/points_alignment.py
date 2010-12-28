import numpy as np
from contracts import contracts, check
from snp_geometry.random_geometry import geodesic_distance_on_S2
from contracts.main import new_contract

@new_contract
@contracts(X='array[KxN],K>0,N>0')
def directions(X):
    ''' Checks that every column has unit length. '''
    K = X.shape[1]
    for i in range(K):
        v = X[:, i]
        np.testing.assert_allclose(1, np.linalg.norm(v))

@contracts(X='array[KxN],K>=2', Y='array[KxN]', returns='array[KxK],orthogonal')
def find_best_orthogonal_transform(X, Y):
    ''' Finds the best orthogonal transform R (R in O(K)) between X and Y,
        such that R X ~= Y. '''
    YX = np.dot(Y, X.T)
    check('array[KxK]', YX)
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
    return average_geodesic_error(X2, Y)

# TODO: add unit test for these
@contracts(X='directions,array[3xN]', Y='directions,array[3xN]',)
def average_geodesic_error(X, Y):
    N = X.shape[1]
    total_error = 0
    for i in range(N):
        x, y = X[:, i], Y[:, i]
        total_error += geodesic_distance_on_S2(x, y) 
    return total_error / N

    
    
    
