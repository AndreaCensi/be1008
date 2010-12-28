from reprep import Report
import numpy as np
from contracts.main import check
    
def plot_CBCt_iterations(results, nid='CBCt_iterations'):
    R = results['R']
    true_C = results['true_C']
    iterations = results['iterations']
    R_order = iterations[0]['R_order']

    true_dist = np.real(np.arccos(true_C))


    r = Report(nid)
    f = r.figure(cols=3, caption='Ground truth')
    with r.data_pylab('r_vs_c') as pylab:
        pylab.plot(true_C.flat, R.flat, '.', markersize=0.2)
        pylab.xlabel('real cosine')
        pylab.ylabel('correlation measure')
        pylab.axis((-1, 1, -1, 1))
    f.sub('r_vs_c', 'Unknown function correlation -> cosine')

    r.data('true_C', true_C).display('posneg', max_value=1).add_to(f, 'ground truth cosine matrix')
    r.data('gt_dist', true_dist).display('scale').add_to(f, 'ground truth distance matrix')

    f.data('R_order', R_order).display('scale').add_to(f, 'Order for R')
    
    fit = r.figure(cols=6)
    
    for i, it in enumerate(iterations):
#       current_guess_for_S = best_embedding_on_sphere(R, ndim)
#        
#        for iteration in range(num_iterations):
#            guess_for_C = get_cosine_matrix_from_s(current_guess_for_S)
#            guess_for_C_sorted = np.sort(guess_for_C.flat)
#            new_estimated_C = guess_for_C_sorted[R_order]
#            new_guess_for_S = best_embedding_on_sphere(new_estimated_C, ndim) 
        # ['ndim', 'R_percentile', 'iteration', 'dont_trust', 'new_guess_for_S', 
        # 'S', 'R', 'current_guess_for_S', 'guess_for_C', 'R_order', 'trust_R_top_perc',
        #  'S_aligned', 'guess_for_C_sorted', 'error_deg', 'num_iterations', 'careful_C', 
        # 'new_estimated_C', 'error']

        rit = r.node('iteration%2d' % i)
        
        def display_posneg(what, caption="no desc"):
            data = it[what]
            nid = what
            n = rit.data(nid, data)
            n.display('posneg', max_value=1)
            fit.sub(n, caption=caption + ' (``%s``)' % what)

        def display_coords(nid, coords, caption=None):    
            n = rit.data(nid, coords)
            with n.data_pylab('plot') as pylab:
                pylab.plot(coords[0, :], coords[1, :], 'k-')
                pylab.plot(coords[0, :], coords[1, :], '.')
                pylab.axis('equal')
            fit.sub(n, caption=caption)

        
        display_coords('current_guess_for_S', it['current_guess_for_S'],
                       'Current guess for coordinates.')
        display_posneg('guess_for_C', 'Cosines corresponding to guess for S.')
        display_posneg('new_estimated_C', 'Current guess for cosine matrix')
        
        if True:
            display_posneg('dont_trust', 'Areas we do not trust.')
            display_posneg('careful_C', 'The updated version of C.')
        
        
        display_coords('new_guess_for_S', it['new_guess_for_S'],
                       'Current guess for coordinates (errors %.2f / %.2f deg)' % 
                       (it['error_deg'], it['rel_error_deg']))
        
        
#         careful_C = new_estimated_C.copy()
#         dont_trust = R_percentile < (100 - trust_R_top_perc)
#            if iteration > 0:
#                careful_C[dont_trust] = guess_for_C[dont_trust]

            
#        rit.data('Cest', it['Cest']).display('posneg', max_value=1).add_to(f, 'Cest')
#        rit.data('dont_trust', it['dont_trust'] * 1.0).display('scale').add_to(f, 'trust')
#        rit.data('Cestn', it['Cestn']).display('posneg', max_value=1).add_to(f, 'Cestn')
#        dist = np.real(np.arccos(it['Cestn']))
#        rit.data('dist', dist).display('scale', max_value=np.pi).add_to(f, 'corresponding distance')

#        distp = propagate(dist)
#        rit.data('distp', distp).display('scale', max_value=np.pi).add_to(f, 'propagated distance')
        
#        n = rit.data('singular_values', singular_values)
#        with n.data_pylab('plot') as pylab:
#            s = singular_values 
#            s = s / s[0]
#            pylab.plot(s[:15], 'x-')
#        f.sub(n, 'Singular values')
        
#
#        n = rit.data('coords_proj', coords)
#        with n.data_pylab('plot') as pylab:
#            pylab.plot(coords_proj[0, :], coords_proj[1, :], '.')
#            pylab.axis((-1, 1, -1, 1))
#        f.sub(n, 'Coordinates (projected)')
#        
#        with n.data_pylab('r_vs_est_c') as pylab:
#            pylab.plot(estimated_C.flat, R.flat, '.', markersize=0.2)
#            pylab.ylabel('estimated cosine')
#            pylab.xlabel('correlation measure')
#            pylab.axis((-1, 1, -1, 1))
#        f.sub('r_vs_est_c', 'R vs estimated C')
#            
#        with n.data_pylab('order_order') as pylab:
#            pylab.plot(estimated_C_order.flat, R_order.flat, '.', markersize=0.2)
#            pylab.ylabel('est C order')
#            pylab.xlabel('R order')
#        f.sub('order_order')
#        
#        
#        # XXX: if mistake: add_child, nothing happens
#        rit.data('estimated_C', estimated_C).display('posneg').add_to(f, 'estimated_C') 
#        
#        rit.data('Cest_new', it['Cest_new']).display('posneg', max_value=1).add_to(f, 'Cest_new')
#        
    return r
