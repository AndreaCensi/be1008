from contracts import contracts, new_contract, decorate

from .calib_1D_stats_plots import get_cosine_matrix_from_s, \
    get_distance_matrix_from_cosine
import numpy as np
import itertools
from be1011.calib_1D_stats_plots import create_s_from_theta
from nose.tools import nottest

# TODO: decorator
class CalibTestCase(object):
    
    @contracts(tcid=str, R='array[NxN]')
    def __init__(self, tcid, R):
        self.tcid = tcid
        self.R = R
        self.has_ground_truth = False

    @contracts(S='array[(2|3)xN]', kernel='None|Callable')        
    def set_ground_truth(self, S, kernel):
        self.has_ground_truth = True
        self.true_S = S
        self.true_C = get_cosine_matrix_from_s(self.true_S)
        self.true_D = get_distance_matrix_from_cosine(self.true_C)
        self.true_kernel = kernel

new_contract('test_case', CalibTestCase)

@nottest
@contracts(returns='list(test_case)')
def get_syntethic_test_cases():
    
    kernels = []
    def k(f):
        signature = dict(x='array(>=-1,<=+1),shape(x)',
                         returns='array(>=-1,<=+1),shape(x)')
        f2 = decorate(f, **signature)
        kernels.append(f2)
        return f2
    
    # Kernels are functions from cosine -> correlation ([-1,1]->[-1,1])
    # The should be able to operate on arrays and return arrays
    def saturate(f, x): return f(np.maximum(0, x))
    
    @k
    def identity(x): return x
    @k
    def identity_sat(x): return saturate(identity, x)
    @k
    def pow3(x): return x ** 3
    @k
    def pow3_sat(x): return saturate(pow3, x)
    @k
    def pow7(x): return x ** 7
    @k
    def pow7_sat(x): return saturate(pow7, x)
    
    # check that we don't have repeated names
    all_names = [f.__name__ for f in kernels]
    assert len(all_names) == len(np.unique(all_names)), \
        'Repeated names for kernels: %s' % all_names
    
    fovs_deg = [ 45, 90, 135, 180, 180 + 45, 270, 270 + 45, 360]
    
    num = 180
    tcs = {}
    # Enforce constraints using signature
    for kernel, fov_deg in itertools.product(kernels, fovs_deg):
        tcid = 'fov%d-%s-noisy' % (fov_deg, kernel.__name__)
        tc = generate_circular_test_case(tcid=tcid,
                                         num=num,
                                         fov=np.radians(fov_deg),
                                         kernel=kernel,
                                         wiggle_std_deg=1,
                                         dist_noise=0.1,
                                         abs_cos_noise_std=0.1)
        tcs[tcid] = tc

        tcid = 'fov%d-%s' % (fov_deg, kernel.__name__)
        tc = generate_circular_test_case(tcid=tcid,
                                         num=num,
                                         fov=np.radians(fov_deg),
                                         kernel=kernel,
                                         wiggle_std_deg=1,
                                         dist_noise=0.01,
                                         abs_cos_noise_std=0.01)
        tcs[tcid] = tc
        
    return tcs

# TODO: add pi
#@contracts(fov='<=2*pi')
@nottest
@contracts(tcid=str, num='int,>0', kernel='Callable', returns='test_case')
def generate_circular_test_case(tcid, fov, num, kernel,
                                wiggle_std_deg=0, dist_noise=0, abs_cos_noise_std=0):
    angles = np.linspace(-fov / 2, fov / 2, num)
    
    # wiggles the angles a little bit
    angles += np.random.randn(num) * np.radians(wiggle_std_deg)
        
    S = create_s_from_theta(angles)
    
    C = get_cosine_matrix_from_s(S)
    # get real distances
    D = np.arccos(C)
    # Multiplicative noise
    noise = np.random.randn(*(D.shape))
    D2 = D + dist_noise * D * noise
    C2 = np.cos(D2)
    
    R = kernel(C2)
    
    # We don't want to mess with the diagonal
    where = R < 5 * abs_cos_noise_std
    R2 = R + where * np.random.randn(*(R.shape)) * abs_cos_noise_std
    
    R2 = np.clip(R2, -1, 1)
    tc = CalibTestCase(tcid, R2)
    tc.set_ground_truth(S, kernel)
    return tc
