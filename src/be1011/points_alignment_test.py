import unittest

import numpy as np

from snp_geometry import random_rotation

from .points_alignment import (find_best_orthogonal_transform,
                               overlap_error_after_orthogonal_transform)
from snp_geometry.random_geometry import random_directions


N = 100
    
class UtilsTests(unittest.TestCase):
        
    def test_find_best_rotation(self):
        for i in range(N): #@UnusedVariable
            X = random_directions(20)
            R = random_rotation()
            Y = np.dot(R, X)
            Rest = find_best_orthogonal_transform(X, Y)
            np.testing.assert_allclose(R, Rest)
            Rest2 = find_best_orthogonal_transform(Y, X)
            np.testing.assert_allclose(R.T, Rest2)
            
    def test_overlap_error(self):
        for i in range(N): #@UnusedVariable
            X = random_directions(20)
            R = random_rotation()
            Y = np.dot(R, X)
            e1 = overlap_error_after_orthogonal_transform(X, Y)
            atol = 1E-7
            np.testing.assert_allclose(e1, 0, atol=atol)
            e2 = overlap_error_after_orthogonal_transform(Y, X)
            np.testing.assert_allclose(e2, 0, atol=atol)
             
