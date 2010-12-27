from contracts import contracts, new_contract, decorate

from .calib_1D_stats_plots import get_cosine_matrix_from_s, \
    get_distance_matrix_from_cosine
import numpy as np
import itertools
from be1011.calib_1D_stats_plots import create_s_from_theta
from nose.tools import nottest

# TODO: decorator
class TestCase(object):
    
    @contracts(name=str, R='array[NxN]')
    def __init__(self, name, R):
        self.name = name
        self.R = R
        self.has_ground_truth = False

    @contracts(S='array[(2|3)xN]', kernel='Callable')        
    def set_ground_truth(self, S, kernel):
        self.has_ground_truth = True
        self.true_S = S
        self.true_C = get_cosine_matrix_from_s(self.true_S)
        self.true_D = get_distance_matrix_from_cosine(self.true_C)
        self.true_kernel = kernel

new_contract('test_case', TestCase)

@nottest
@contracts(returns='list(test_case)')
def get_syntethic_test_cases():
    
    kernels = []
    def k(f):
        signature = dict(x='array[NxN](>=-1,<=+1)',
                         returns='array[NxN](>=-1,<=+1)')
        f2 = decorate(f, **signature)
        kernels.append(f2)
        return f2
    
    # Kernels are functions from cosine -> correlation ([-1,1]->[-1,1])
    # The should be able to operate on arrays and return arrays
    def saturate(f, x): return np.maximum(0, f(x))
    
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
    
    
    fovs_deg = [ 45, 90, 135, 180, 180 + 45, 270, 270 + 45, 360]
    
    num = 180
    tcs = []
    # Enforce constraints using signature
    for kernel, fov_deg in itertools.product(kernels, fovs_deg):
        tcid = 'fov%d-%s' % (fov_deg, k.__name__)
        tc = generate_circular_test_case(tcid=tcid,
                                         num=num,
                                         fov=np.radians(fov_deg),
                                         kernel=kernel)
        tcs.append(tc)
        
    return tcs

# TODO: add pi
#@contracts(fov='<=2*pi')
@nottest
@contracts(tcid=str, num='int,>0', kernel='Callable', returns=TestCase)
def generate_circular_test_case(tcid, fov, num, kernel):
    angles = np.linspace(-fov / 2, fov / 2, num)
    S = create_s_from_theta(angles)
    C = get_cosine_matrix_from_s(S)
    R = kernel(C)
    tc = TestCase(tcid, R)
    tc.set_ground_truth(S, kernel)
    return tc
