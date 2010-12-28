import cPickle as pickle
from optparse import OptionParser
import os
import numpy

from reprep import Report
from contracts import contracts, check
from procgraph_statistics.cov2corr import cov2corr

from .calibrator_plots import OpenStruct
from .generic_bgds_boot_plots import scale_score

def main():
    parser = OptionParser()

    parser.add_option("--file", help='Pickle file')
    parser.add_option("--outdir")

    (options, args) = parser.parse_args() #@UnusedVariable
    assert not args
    

    data = pickle.load(open(options.file, 'rb'))
    
    select = range(181)
    
    for x in ['y_cov', 'y_dot_cov', 'y_dot_sign_cov']:
        data[x] = data[x][select, :][:, select]
        check('array[NxN]', data[x])
    
    n = data['y_cov'].shape[0]
    #theta = numpy.linspace(0, numpy.pi * 2, n)
    theta = numpy.linspace(0, numpy.pi, n)    
    
    d = OpenStruct(**data) 
    
    # groundtruth 
    d.theta = theta
    d.S = create_s_from_theta(d.theta)
    d.C = get_cosine_matrix_from_s(d.S)
    d.D = get_distance_matrix_from_cosine(d.C)

    r = Report('calibrator_analysis')
    
    #r.add_child(simple_plots(d))
    #r.add_child(ground_truth_plots(d))
    #r.add_child(hist_plots(d))
    r.add_child(iterations_plots(d))
    
    filename = os.path.join(options.outdir, 'calib_1d_stats_plots.html')
    print("Writing to %r" % filename)
    r.to_html(filename)

@contracts(theta='array[N]', returns='array[3xN]')
def create_s_from_theta(theta):
    return numpy.vstack((numpy.cos(theta), numpy.sin(theta), 0 * theta))

@contracts(S='array[KxN],K<N', returns='array[NxN]')
def get_cosine_matrix_from_s(S):
    C = numpy.dot(S.T, S)
    return numpy.clip(C, -1, 1, C)

@contracts(C='array[NxN](>=-1,<=1)', returns='array[NxN]')
def get_distance_matrix_from_cosine(C):
    return numpy.real(numpy.arccos(C))

def ground_truth_plots(d):
    r = Report()
    f = r.figure(cols=3)

    n = r.data('cosine', d.C).display('posneg')  
    f.sub(n, 'Cosine matrix')
    
    n = r.data('dist', d.D).display('scale')  
    f.sub(n, 'Distance matrix')
    
    return r

def simple_plots(d):
    # TO
    y_cov = d.y_cov
    y_dot_cov = d.y_dot_cov
    y_dot_sign_cov = d.y_dot_sign_cov
    
    vars = [ ('y', y_cov, {}),
             ('y_dot', y_dot_cov, {}),
             ('y_dot_sign', y_dot_sign_cov, {}) ] 
#
#    I = numpy.eye(y_cov.shape[0])
#    
    r = Report()
    f = r.figure(cols=3)
    for var in vars:
        label = var[0]
        cov = var[1]
        corr = cov2corr(cov, zero_diagonal=False)
        corr_z = cov2corr(cov, zero_diagonal=True)
        
        n1 = r.data("cov_%s" % label, cov).display('posneg')
        n2 = r.data("corr_%s" % label, corr).display('posneg')
        n3 = r.data("corrz_%s" % label, corr_z).display('posneg')
        
        f.sub(n1, 'Covariance of %s' % label)
        f.sub(n2, 'Correlation of %s ' % label)
        f.sub(n3, 'Correlation of %s (zeroing diagonal)' % label)
        
    return r
    
     
def hist_plots(d):
    # TO
    vars = [ ('C', d.C, {}),
             ('y', cov2corr(d.y_cov, False), {}),
             ('y_dot', cov2corr(d.y_dot_cov, False), {}),
             ('y_dot_sign', cov2corr(d.y_dot_sign_cov, False), {}) ] 

    r = Report()
    f = r.figure(cols=5)
    
    for var in vars:
        label = var[0]
        x = var[1]

        nid = "hist_%s" % label
        with r.data_pylab(nid) as pylab:
            pylab.hist(x.flat, bins=128)
        f.sub(nid, 'histogram of correlation of %s' % label)
            
        order = scale_score(x)
        r.data('order%s' % label, order).display('posneg').add_to(f, 'ordered')

        nid = "hist2_%s" % label
        with r.data_pylab(nid) as pylab:
            pylab.plot(x.flat, order.flat, '.', markersize=0.2)
            pylab.xlabel(label)
            pylab.ylabel('order')
        f.sub(nid, 'histogram of correlation of %s' % label)
        
        h = create_histogram_2d(d.C, x, resolution=128)
        r.data('h2d_%s' % label, numpy.flipud(h.T)).display('scale').add_to(f)
        
    return r

def create_histogram_2d(x, y, resolution):
    edges = numpy.linspace(-1, 1, resolution)
    H, xe, ye = numpy.histogram2d(x.flatten(), y.flatten(), bins=(edges, edges)) #@UnusedVariable
    return H

def iterations_plots(d):
    
    r = Report('algorithmic_results')
    
    
    # dummy = d.C ** 5  # -- perfect!
    dummy = numpy.maximum(0, d.C ** 7)
    results = cbc(dummy, num_iterations=5, ground_truth=d)
    r.add_child(plot_results('dummy', results))

#    
    y_corr = cov2corr(d.y_cov, False)
    results = cbc(y_corr, num_iterations=5, ground_truth=d)
    r.add_child(plot_results('y_corr', results))
#    
#    y_dot_corr = cov2corr(d.y_dot_cov, False)
#    results = cbc(y_dot_corr, num_iterations=5, ground_truth=d)
#    r.add_child(plot_results('y_dot_corr', results))
    
    y_dot_sign_corr = cov2corr(d.y_dot_sign_cov, False)
    results = cbc(y_dot_sign_corr, num_iterations=5, ground_truth=d)
    r.add_child(plot_results('y_dot_sign_corr', results))
    
    return r
    
def plot_results(label, results):
    iterations = results['iterations']
    r = Report(label)
    
    R = results['R']
    gt_C = results['gt_C']
    f = r.figure(cols=3, caption='Ground truth')
    with r.data_pylab('r_vs_c') as pylab:
        pylab.plot(gt_C.flat, R.flat, '.', markersize=0.2)
        pylab.xlabel('real cosine')
        pylab.ylabel('correlation measure')
        pylab.axis((-1, 1, -1, 1))
    f.sub('r_vs_c', 'Unknown function correlation -> cosine')

    r.data('gt_C', gt_C).display('posneg', max_value=1).add_to(f, 'ground truth cosine matrix')
    
    dist = numpy.real(numpy.arccos(gt_C))
    r.data('gt_dist', dist).display('scale').add_to(f, 'ground truth distance matrix')
    
    f = r.figure(cols=12)
    
    R = results['R']
    R_order = results['R_order']
    
    for i, it in enumerate(iterations):
        singular_values = it['singular_values']
        coords = it['coords']
        coords_proj = it['coords_proj']
        estimated_C = it['estimated_C']
        estimated_C_order = it['estimated_C_order']
        
        check('array[MxN],(M=2|M=3)', coords)
        
        rit = r.node('iteration%2d' % i)
        
        rit.data('Cest', it['Cest']).display('posneg', max_value=1).add_to(f, 'Cest')
        rit.data('dont_trust', it['dont_trust'] * 1.0).display('scale').add_to(f, 'trust')
        rit.data('Cestn', it['Cestn']).display('posneg', max_value=1).add_to(f, 'Cestn')
        dist = numpy.real(numpy.arccos(it['Cestn']))
        rit.data('dist', dist).display('scale', max_value=numpy.pi).add_to(f, 'corresponding distance')
        distp = propagate(dist)
        rit.data('distp', distp).display('scale', max_value=numpy.pi).add_to(f, 'propagated distance')
        
        n = rit.data('singular_values', singular_values)
        with n.data_pylab('plot') as pylab:
            s = singular_values 
            s = s / s[0]
            pylab.plot(s[:15], 'x-')
        f.sub(n, 'Singular values')
        
        n = rit.data('coords', coords)
        with n.data_pylab('plot') as pylab:
            pylab.plot(coords[0, :], coords[1, :], '.')
            pylab.axis('equal')
        f.sub(n, 'Coordinates')

        n = rit.data('coords_proj', coords)
        with n.data_pylab('plot') as pylab:
            pylab.plot(coords_proj[0, :], coords_proj[1, :], '.')
            pylab.axis((-1, 1, -1, 1))
        f.sub(n, 'Coordinates (projected)')
        
        with n.data_pylab('r_vs_est_c') as pylab:
            pylab.plot(estimated_C.flat, R.flat, '.', markersize=0.2)
            pylab.ylabel('estimated cosine')
            pylab.xlabel('correlation measure')
            pylab.axis((-1, 1, -1, 1))
        f.sub('r_vs_est_c', 'R vs estimated C')
            
        with n.data_pylab('order_order') as pylab:
            pylab.plot(estimated_C_order.flat, R_order.flat, '.', markersize=0.2)
            pylab.ylabel('est C order')
            pylab.xlabel('R order')
        f.sub('order_order')
        
        
        # XXX: if mistake: add_child, nothing happens
        rit.data('estimated_C', estimated_C).display('posneg').add_to(f, 'estimated_C') 
        
        rit.data('Cest_new', it['Cest_new']).display('posneg', max_value=1).add_to(f, 'Cest_new')
        
    return r



@contracts
def cbc(R, num_iterations=5, ground_truth=None):
    '''
        :type R: array[NxN]
        :type num_iterations: int,>0
        
        :rtype: dict
    '''
#    N = cbc.N
    
    iterations = []
    
    R_order = scale_score(R).astype('int32')
    estimated_C = R
    Cest = R
    n = R.shape[0]
    
    for iteration in range(num_iterations):
        print('Iteration %d/%d' % (iteration, num_iterations))
        Cestn = Cest.copy()
        #dont_trust = numpy.logical_or(Cestn <= 0.8, R <= 0.8)  
        
        if iteration > 0:
            dont_trust = Cestn <= numpy.cos(numpy.deg2rad(5))
            #Cestn[dont_trust] = estimated_C[dont_trust]
            # Cestn[dont_trust] = -1
        else:
            dont_trust = Cestn <= 10 # visualization
            
        numpy.clip(Cestn, -1, 1, Cestn)
        U, S, V = numpy.linalg.svd(Cestn, full_matrices=0)

        check('array[NxN]', U)
        check('array[N]', S)
        check('array[NxN]', V)
        
#        if iteration == 0:
#            coords = V[[0, 2], :]
#        else:
        nvars = 2

        coords = V[:nvars, :]
        
        
        #check('array[2xN]', coords)
         
        
        for i in range(nvars):
            coords[i, :] = coords[i, :]  * numpy.sqrt(S[i])

        # remove mean
#        if iteration == 0:
#            for i in range(2):
#                coords[i, :] -= coords[i, :].mean() 
        
        # project onto the sphere
        nvars_project = 2
        coords_proj = coords.copy()
        for k in range(n):
            v = coords_proj[:, k]
            coords_proj[:, k] = v / numpy.linalg.norm(v[:nvars_project]) 

        estimated_C = numpy.dot(coords_proj.T, coords_proj)

        # find the best fit g() to
        #    estimated_C = g( R )
        estimated_C_order = scale_score(estimated_C)
        
        estimated_C_sorted = numpy.sort(estimated_C.flat)

        Cest_new = estimated_C_sorted[R_order]

        iteration = dict(Cest=Cest.copy(),
                         dont_trust=dont_trust.copy(),
                         Cestn=Cestn.copy(),
                         singular_values=S.copy(),
                         coords=coords.copy(),
                         coords_proj=coords_proj.copy(),
                         estimated_C=estimated_C.copy(),
                         estimated_C_order=estimated_C_order.copy(),
                         Cest_new=Cest_new.copy())
        
        Cest = Cest_new
        iterations.append(iteration)
    
    #result = numpy.zeros((3, N))
    
    results = dict(R=R, R_order=R_order,
                   gt_C=ground_truth.C,
                   gt_D=ground_truth.D,
                   gt_S=ground_truth.S,
                   iterations=iterations)

    return results



def propagate(D):
    
    # d(a, b) <= d(a,c) + d(a,b)
    n = D.shape[0]
    for i in range(n):
        # conceptually:
        # D[a,b] = numpy.minimum(D[a,b], D[a,i] + D[i,b])
        # we need:
        # M[a,b] = D[a,i] + D[i,b]
        # the two terms are transposed of each other
        # K = D[a,i];  D[i,b] = K'
        col = D[:, i]
        K = numpy.tile(col, (n, 1)).T
        assert K.shape == (n, n), K.shape
        assert (K[:, 3] == col).all()
        
        KK = K + K.T
        D = numpy.minimum(D, KK)
        
    return D
    
