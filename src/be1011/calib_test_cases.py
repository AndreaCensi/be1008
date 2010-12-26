from contracts import contracts, new_contract

from .calib_1D_stats_plots import get_cosine_matrix_from_s, \
    get_distance_matrix_from_cosine
import numpy
import random
import math


class TestCase(object):
    
    @contracts(name=str, R='array[NxN]')
    def __init__(self, name, R):
        self.name = name
        self.R = R
        self.has_ground_truth = False

    @contracts(S='array[(2|3)xN]')        
    def set_ground_truth(self, S):
        self.has_ground_truth = True
        self.true_S = S
        self.true_C = get_cosine_matrix_from_s(self.true_S)
        self.true_D = get_distance_matrix_from_cosine(self.true_C)

