from contracts import check_multiple, contracts
import numpy as np
from .points_alignment import find_best_orthogonal_transform, \
    overlap_error_after_orthogonal_transform
from be1011.generic_bgds_boot_plots import scale_score
from be1011.calib_1D_stats_plots import get_cosine_matrix_from_s, \
    get_distance_matrix_from_cosine
from contracts.main import check

class CalibAlgorithm(object):
    
    def __init__(self, params):
        self.params = params
    
    def solve(self, R, true_S=None):
        self.R = R
        self.iterations = []
        self.true_S = true_S
        if true_S is not None:
            check('directions', true_S)
        self._solve(R)
        self.n = R.shape[0]
        
        last_iteration = self.iterations[-1]
        results = {}
        copy_fields = ['error', 'error_deg', 'S', 'S_aligned']
        for f in copy_fields:
            results[f] = last_iteration[f]
        
        results['R'] = R    
        results['n'] = R.shape[0]
        results['params'] = self.params
        results['true_S'] = true_S
        if true_S is not None:
            results['true_C'] = get_cosine_matrix_from_s(true_S)
            results['true_dist'] = get_distance_matrix_from_cosine(results['true_C'])
            
        results['iterations'] = self.iterations
            
        self.results = results
        return self.results
    
    def iteration(self, data):
        for x in ['self']: 
            if x in data: del data[x]
        
        S = data['S']
        check_multiple([('array[NxN]', self.R), ('array[*xN]', S)])
            
        check('directions', S)
            
        # compute measures here
        if self.true_S is not None:
            
            # add more rows to S if necessary
            K = S.shape[0]
            if K != self.true_S.shape[0]:
                newS = np.zeros(self.true_S.shape)
                newS[:K, :] = S
                newS[K:, :] = 0
                S = newS
                check('directions', S)

            Rest = find_best_orthogonal_transform(S, self.true_S)
            data['S_aligned'] = np.dot(Rest, S)
            data['error'] = \
                overlap_error_after_orthogonal_transform(S, self.true_S)
            data['error_deg'] = np.degrees(data['error'])
            
            data['rel_error'] = compute_relative_error(self.true_S, S, 10)
            data['rel_error_deg'] = np.degrees(data['rel_error'])
            
            print('Iteration %d: error %.3f  relative %.3f ' % 
                  (len(self.iterations), data['error_deg'], data['rel_error_deg']))
        else:
            print('Iteration %d' % len(self.iterations))
            
        self.iterations.append(data)

    def param(self, name, value, desc=None):
        self.params[name] = value
        
    def __str__(self):
        params = "-".join('%s=%s' % (k, v) for k, v in self.params.items()) 
        return '%s(%s)' % (self.__class__.__name__, params)
            
def compute_relative_error(true_S, S, neighbours_deg=20):
    ''' Returns the average error in radians between points. '''
    true_C = get_cosine_matrix_from_s(true_S)
    true_D = np.arccos(true_C)
    valid = true_D < np.radians(neighbours_deg)

    C = get_cosine_matrix_from_s(S)
    D = np.arccos(C)
    
    nvalid = (1 * valid).sum()
    errors = np.abs((D - true_D))
    errors_sum = (errors * valid).sum()
    
    average_error = errors_sum / nvalid
    return average_error
    
    
    # get real distancescompute_orthog            

@contracts(S='array[KxN],K<N', returns='array[KxN]')
def project_vectors_onto_sphere(S, atol=1e-7):
    K, N = S.shape
    coords_proj = np.zeros((K, N))
    for i in range(N):
        v = S[:, i]
        nv = np.linalg.norm(v)
        if np.fabs(nv) < atol:
            raise ValueError('Vector too small: %s' % v)
        coords_proj[:, i] = v / nv
    return coords_proj

class Random(CalibAlgorithm):
    ''' This is used for debugging. Provides a random guess. '''
    
    def _solve(self, R):
        ndim = self.params['ndim']
        N = R.shape[0]
        X = np.random.randn(ndim, N)
        guess = project_vectors_onto_sphere(X)
        self.iteration(dict(S=guess))


class Cheater(CalibAlgorithm):
    ''' This is used for debugging. It cheats by
        looking at the ground truth and applies a random rotation. '''
    
    def _solve(self, R): #@UnusedVariable
        if self.true_S is not None:
            # TODO: add general orthogonal transform
            guess = -self.true_S 
        else:
            assert False

        results = dict(S=guess)
        self.iteration(results)



class OneShotEmbedding(CalibAlgorithm):
    
    def _solve(self, R):
        ndim = self.params['ndim']
        S = best_embedding_on_sphere(R, ndim)
        self.iteration(dict(S=S))

@contracts(R='array[NxN]', ndim='int,K', returns='array[KxN],directions')
def best_embedding_on_sphere(R, ndim):
    coords = best_embedding(R, ndim)
    proj = project_vectors_onto_sphere(coords)
    return proj

@contracts(R='array[NxN]', ndim='int,K', returns='array[KxN]')
def best_embedding(R, ndim):
    U, S, V = np.linalg.svd(R, full_matrices=0)
    check_multiple([ ('array[NxN]', U),
                     ('array[N]', S),
                     ('array[NxN]', V) ])
    coords = V[:ndim, :]
    for i in range(ndim):
        coords[i, :] = coords[i, :]  * np.sqrt(S[i])
    return coords

class CBC(CalibAlgorithm):
    def _solve(self, R):
        ndim = self.params['ndim']
        num_iterations = self.params['num_iterations']
        
        # Score of each datum -- must be computed only once
        R_order = scale_score(R).astype('int32')

        M = (R_order * 2.0 / (R.size - 1)) - 1
        np.testing.assert_almost_equal(M.max(), +1)
        np.testing.assert_almost_equal(M.min(), -1)
        current_guess_for_S = best_embedding_on_sphere(M, ndim)

        for iteration in range(num_iterations):
            guess_for_C = get_cosine_matrix_from_s(current_guess_for_S)
            guess_for_C_sorted = np.sort(guess_for_C.flat)
            new_estimated_C = guess_for_C_sorted[R_order]
            new_guess_for_S = best_embedding_on_sphere(new_estimated_C, ndim) 
            
            data = dict(S=new_guess_for_S, **locals())
            self.iteration(data)
            
            current_guess_for_S = new_guess_for_S
            
class CBCt(CalibAlgorithm):
    def _solve(self, R):
        ndim = self.params['ndim']
        num_iterations = self.params['num_iterations']
        trust_R_top_perc = self.params['trust_R_top_perc']
        check('>0,<100', trust_R_top_perc)
        
        # Score of each datum -- must be computed only once
        R_order = scale_score(R).astype('int32')
        R_percentile = R_order * 100.0 / R_order.size
        
        M = (R_order * 2.0 / (R.size - 1)) - 1
#        M = ((R_order + 1) * 2.0 / R.size) - 1.0
        np.testing.assert_almost_equal(M.max(), +1)
        np.testing.assert_almost_equal(M.min(), -1)

        current_guess_for_S = best_embedding_on_sphere(M, ndim)
        
        for iteration in range(num_iterations):
            guess_for_C = get_cosine_matrix_from_s(current_guess_for_S)
            guess_for_C_sorted = np.sort(guess_for_C.flat)
            new_estimated_C = guess_for_C_sorted[R_order]
            
            careful_C = new_estimated_C.copy()
            dont_trust = R_percentile < (100 - trust_R_top_perc)
            if iteration > 0:
                careful_C[dont_trust] = guess_for_C[dont_trust]
#                careful_C[dont_trust] = -1 # good for fov 360
#                careful_C[dont_trust] = 0
                

            new_guess_for_S = best_embedding_on_sphere(careful_C, ndim) 
            
            data = dict(S=new_guess_for_S, **locals())
            self.iteration(data)
            
            current_guess_for_S = new_guess_for_S
            
    # Prove fixed point:
    # :: guess_for_S = true_S
    # guess_for_C = get_cosine_matrix_from_s(guess_for_S)
    # :: guess_for_C = true_C
    # guess_for_C_sorted = np.sort(guess_for_C.flat)
    # :: guess_for_C_sorted = sort(true_C)
    # new_estimated_C = guess_for_C_sorted[R_order]
    # :: new_estimated_C = (sort(true_C))[R_order]
    #    by assumption (R=g(C), g monotone), we have R_order = C_order
    # :: new_estimated_C = (sort(true_C))[order(true_C)]
    #    For all vectors x, sort(x)[order(x)] = x
    # :: new_estimated_C = true_C
    #    new_guess_for_S = best_embedding_on_sphere(new_estimated_C, ndim)
    # :: new_guess_for_S = best_embedding_on_sphere(true_C, ndim)
    #    new_guess_for_S = true_S


class CBCt2(CalibAlgorithm):
    def _solve(self, R):
        ndim = self.params['ndim']
        num_iterations = self.params['num_iterations']
#        trust_R_top_perc = self.params['trust_R_top_perc']
#        check('>0,<100', trust_R_top_perc)
        
        # Score of each datum -- must be computed only once
        R_order = scale_score(R).astype('int32')
        R_percentile = R_order * 100.0 / R_order.size
        
        M = (R_order * 2.0 / (R.size - 1)) - 1.0
        np.testing.assert_almost_equal(M.max(), +1)
        np.testing.assert_almost_equal(M.min(), -1)
        current_guess_for_S = best_embedding_on_sphere(M, ndim)
        
        time = [100, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 100, 100]
        for iteration in range(len(time)):
            guess_for_C = get_cosine_matrix_from_s(current_guess_for_S)
            guess_for_C_sorted = np.sort(guess_for_C.flat)
            new_estimated_C = guess_for_C_sorted[R_order]
            
            careful_C = new_estimated_C.copy()
            
            trust_R_top_perc = time[iteration]
            dont_trust = R_percentile < (100 - trust_R_top_perc)
            careful_C[dont_trust] = guess_for_C[dont_trust]
#                careful_C[dont_trust] = -1 # good for fov 360
#                careful_C[dont_trust] = 0
                

            new_guess_for_S = best_embedding_on_sphere(careful_C, ndim) 
            
            data = dict(S=new_guess_for_S, **locals())
            self.iteration(data)
            
            current_guess_for_S = new_guess_for_S
         
