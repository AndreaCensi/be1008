import os
import itertools
import numpy as np
import cPickle as pickle
from optparse import OptionParser

from reprep import Report

from procgraph_statistics.cov2corr import cov2corr
from contracts import check, contracts, new_contract

from .calib_test_cases import get_syntethic_test_cases
from .calib_1D_stats_plots import create_s_from_theta, create_histogram_2d
from .calib_test_cases import CalibTestCase
from .generic_bgds_boot_plots import scale_score

from .calib_algos import OneShotEmbedding, Cheater, Random
from be1011.calib_algos import CBC, CBCt, CBCt2
from be1011.natsort import natsorted
from be1011.calib_plots_and_stats import plot_CBCt_iterations
from collections import namedtuple
from compmake.jobs.syntax.parsing import expand_wildcard
from compmake import comp

join = os.path.join

def main():
    
    parser = OptionParser()

    parser.add_option("--data", help='.pickle file containing data.')

    parser.add_option("--outdir", help='Directory with variables.pickle and where '
                                    'the output will be placed.')

    (options, args) = parser.parse_args() #@UnusedVariable
    assert not args
    assert options.data is not None 
    assert options.outdir is not None 
    
    print('Generating syntethic test cases...')
    synthetic = get_syntethic_test_cases()
    
    print('Reading real data...')
    data = pickle.load(open(options.data, 'rb'))
    real = get_real_test_cases(data)
    test_cases = {}
    test_cases.update(synthetic)
    test_cases.update(real)

    print('Creating list of algorithms..')
    algorithms = get_list_of_algorithms()    
    check('dict(str: tuple(Callable, dict))', algorithms)

    print('Creating list of combinations..')
    combinations = {}
    Combination = namedtuple('Combination', 'algorithms test_cases')
    combinations['all'] = Combination('*', '*')
    combinations['CBC'] = Combination(['cbc'], '*')
    combinations['CBCt'] = Combination('cbct*', '*')
    combinations['tmp'] = Combination('cbc*', ['fov180-pow7*', 'fov360-pow7*'])

    # set of tuple (algo, test_case)
    executions = {}
    
    def expand(x, options):
        if isinstance(x, list):
            return sum([expand(y) for y in x])
        elif isinstance(x, str):
            if '*' in x:
                return [expand_wildcard(x, options)]
            else:
                return [x]
    
    def stage_execution(tcid, algid):
        key = (tcid, algid)
        if not key in executions:
            test_case = test_cases[tcid]
            algo_class, algo_params = algorithms[algid]
            job_id = 'run-%s-%s' % (tcid, algid)
            results = comp(run_combination, test_case, algo_class, algo_params,
                            job_id=job_id)
            executions[key] = results
        return executions[key]
        
    
    for comb_id, comb in combinations:
        alg_ids = expand(comb.algorithms, algorithms.keys())
        tc_ids = expand(comb.test_cases, test_cases.keys())
        
        deps = {}
        for t, a in itertools.product(tc_ids, alg_ids):
            deps[(t, a)] = stage_execution(t, a)
    
        job_id = 'report_comb_stats-%s' % comb_id
        report = comp(report_comb_stats, comb_id, tc_ids, alg_ids, deps, job_id=job_id)
        
        filename = join(options.outdir, 'stats', '%s.html' % comb_id)
        comp(write_report, report, filename)

#    display_problem_instances(use_tc, 'use_tc', prefix=join(options.outdir, 'statistics'))
#    
#    results = {}
#    for tc, algo in itertools.product(use_tc, use_algorithms):
#        algid, algo_class, algo_params = algo
#        results[(tc.tcid, algid)] = run_combination(tc, algo_class, algo_params) 
#    
#    
#    display_stats(results, setid, prefix=join(options.outdir, 'statistics'))
#    display_iterations(results, prefix=join(options.outdir, 'iterations'))
#    

def write_report(report, filename):
    print('Writing to %r.' % filename)
    report.to_html(filename)


def run_combination(test_case, algo_class, algo_params):
    print('Running %s - %s(%s)' % (test_case.tcid, algo_class.__name__, algo_params))
    algo = algo_class(algo_params)
    if test_case.has_ground_truth:
        algo.solve(R=test_case.R, true_S=test_case.true_S)
    else:
        algo.solve(R=test_case.R)
        
    results = algo.results
    
    other = {'test_case': test_case,
             'algo_class': algo_class,
             'combid': '%s-%s' % (test_case.tcid, algo) }
    
    results.update(other)
    return results

    
def get_list_of_algorithms():
    its = 6
    return dict([
            ('cheat', (Cheater, {'ndim': 2})) ,
            ('rand', (Random, {'ndim': 2})),
            ('cbct2', (CBCt2, {'ndim': 2, 'num_iterations': 10})),
            ('cbc75', (CBCt, {'ndim': 2, 'num_iterations': its, 'trust_R_top_perc': 75})),
            ('cbc50', (CBCt, {'ndim': 2, 'num_iterations': its, 'trust_R_top_perc': 50})),
            ('cbc20', (CBCt, {'ndim': 2, 'num_iterations': its, 'trust_R_top_perc': 20})),
            ('cbc5', (CBCt, {'ndim': 2, 'num_iterations': its, 'trust_R_top_perc': 10})),
            ('cbc', (CBC, {'ndim': 2, 'num_iterations': its})),
            ('embed2', (OneShotEmbedding, {'ndim': 2})),
        ])
    
def display_iterations(results, prefix):
    for combination, result in results.items():
        algo_class = result['algo_class'] 
        if algo_class in[ CBCt, CBCt2]:
            r = plot_CBCt_iterations(result)
            filename = os.path.join(prefix, 'iterations', '%s-%s.html' % combination)
            print('Writing to %r.' % filename)
            r.to_html(filename)
        else:
            print('Cannot plot algo %s' % algo_class)


def display_stats(results, setid, prefix):
    r = Report(setid)
    
#    data, rlabels, clabels = algo_stats_A(results.values())
    
    data, rlabels, clabels = algo_stats_error_table(results)
    
    r.table('stats', data, rows=rlabels, cols=clabels)
    
    filename = os.path.join(prefix, '%s.html' % r.id)
    print('Writing to %r.' % filename)
    resources = os.path.join(prefix, 'data')
    r.to_html(filename, resources_dir=resources)
    return r


new_contract('header', 'None|str')
new_contract('table_desc', '''tuple(list[R](list[C]),list[R](header),list[C](header))''')

@contracts(results='list(dict)', returns='table_desc')
def algo_stats_A(results):
    rows_labels = []
    data = []
    cols_labels = ['combination', 'average error (deg)']
    for r in results:
        row = [r['combid'],
               "%.2f" % r['results']['error_deg']]
        rows_labels.append(None)
        data.append(row)
        
    return data, rows_labels, cols_labels 
    
def algo_stats_error_table(results):
    all_tc = natsorted(set([tc for tc, algo in results.keys()]), key=lambda x: str(x))
    all_algo = natsorted(set([algo for tc, algo in results.keys()]))

#    rows = [tc.tcid for tc in all_tc]
#    cols = ['%s-%s' % (algo[0].__name__, algo[1]) for algo in all_algo]
    rows = all_tc
    cols = all_algo
    
    def element(res):
        return '%.2f' % res['error_deg']
    
    data = [ [ element(results[(tc, algo)]) 
               for algo in all_algo ] 
             for tc in all_tc]
     
    return data, rows, cols        


def display_problem_instances(tcs, setid, prefix):
    if not os.path.exists(prefix):
        os.makedirs(prefix)
        
    resources = os.path.join(prefix, 'data')
    
    rall = Report(setid)
    for tc in tcs:
        r = Report(tc.tcid)
        r.add_child(tc_problem_plots(tc)) 
        if tc.has_ground_truth:
            r.add_child(tc_ground_truth_plots(tc))

        filename = os.path.join(prefix, '%s.html' % tc.tcid)
        print('Writing to %r.' % filename)
        r.to_html(filename, resources_dir=resources)
        rall.add_child(r)
        
    filename = os.path.join(prefix, '%s.html' % rall.id)
    print('Writing to %r.' % filename)
    rall.to_html(filename, resources_dir=resources)
    return rall

def tc_problem_plots(tc, rid='problem_data'):
    r = Report(rid)
    R = tc.R
    n = R.shape[0]
    # zero diagonal
    Rz = (1 - np.eye(n)) * R
    
    f = r.figure(cols=3)
    
    r.data("Rz", Rz).display('posneg')
    f.sub('Rz', caption='The given correlation matrix (diagonal set to 0)')
    
    return r
    
def tc_ground_truth_plots(tc, rid='ground_truth'):
    r = Report(rid)
    assert tc.has_ground_truth
    
    cols = 4
    if tc.true_kernel is not None:
        cols += 1
    
    f = r.figure(cols=cols, caption='Ground truth plots.')

    n = r.data('true_C', tc.true_C).display('posneg')  
    f.sub(n, 'Actual cosine matrix')
    
    n = r.data('true_D', tc.true_D).display('scale')  
    f.sub(n, 'Actual distance matrix')
    
    n = plot_one_against_the_other(r, 'true_CvsR', tc.true_C, tc.R)
    f.sub(n, 'Sample histogram')
    
    true_C_order = scale_score(tc.true_C)
    R_order = scale_score(tc.R)
    with r.data_pylab('linearity') as pylab:
        x = true_C_order.flat
        y = R_order.flat
        pylab.plot(x, y, '.', markersize=0.2)
        pylab.xlabel('true_C score')
        pylab.ylabel('R score')
        
    f.sub('linearity', 'Linearity plot (the closer this is to a line, the better '
                        'we can solve)')
    
    if tc.true_kernel is not None:
        x = np.linspace(-1, 1, 512)
        y = tc.true_kernel(x)
        with r.data_pylab('kernel') as pylab:
            pylab.plot(x, y)
            pylab.xlabel('cosine')
            pylab.ylabel('correlation')
            pylab.axis((-1, 1, -1, 1))
        f.sub('kernel', caption='Actual analytical kernel')
    
    return r


def plot_one_against_the_other(r, nid, xval, yval):
    h = create_histogram_2d(xval, yval, resolution=128)
    n = r.data(nid, np.flipud(h.T)).display('scale')
    return n 

    

@contracts(data=dict, returns='dict(str, test_case)')
def get_real_test_cases(data):
    # two types
    selections = [ ('front', np.array(range(181))),
                   ('rear', np.array(range(181, 362))),
                   ('both', np.array(range(362))) ]
    
    # four different statistics
    def stat(var):
        x = data['%s_cov' % var]
        R = cov2corr(x, False)
        return (var, R)
    
    statistics = [ stat('y'),
                   stat('y_dot'),
                   stat('y_dot_sign'),
                   stat('y_dot_abs')]
    
    check('list(tuple(str, $(array[M], M>0, M<=362) ))', selections)
    check('list(tuple(str, array[362x362]))', statistics)
    
    ground_truth = np.linspace(0, np.pi * 2, 362)
    
    tcs = {}
    for sel, stat in itertools.product(selections, statistics):
        selid, select = sel
        statid, bigR = stat
        
        R = bigR[select, :][:, select]
        
        angles = ground_truth[select]
        S = create_s_from_theta(angles)
        
        tcid = '%s-%s' % (selid, statid)
        tc = CalibTestCase(tcid, R)
        tc.set_ground_truth(S, kernel=None)
        
        tcs[tcid] = tc
        
    return tcs

try:
    frozenset
except NameError:
    from sets import ImmutableSet as frozenset

class frozendict(dict):
    __slots__ = ('_hash',)
    def __hash__(self):
        rval = getattr(self, '_hash', None)
        if rval is None:
            rval = self._hash = hash(frozenset(self.iteritems()))
        return rval
    
if __name__ == '__main__':
    main()
