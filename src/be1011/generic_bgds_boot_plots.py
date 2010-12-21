import itertools
import numpy
import scipy.linalg
import os
import cPickle as pickle
from optparse import OptionParser

from reprep import Report

from .calibrator_plots import OpenStruct

def main():    
    parser = OptionParser()
    
    parser.add_option("--outdir",
                  type="string", help='Directory containing data')

    (options, args) = parser.parse_args() #@UnusedVariable
    assert not args
    
    variables = os.path.join(options.outdir, 'results.pickle.part')
    
    data = pickle.load(open(variables, 'rb'))
    
    d = OpenStruct(**data)
    d.P_inv = get_information_matrix(d.P)
    d.Gn = normalize_G(d.G, d.P_inv)
    d.Q_inv = numpy.linalg.pinv(d.Q)
    d.Gnn = normalize_input(d.Gn, d.Q_inv)

    r = Report('boot')    
    r.add_child(cov_plots(d))
    r.add_child(basic_plots(d))
    
    dir = os.path.join(options.outdir, 'plots')
    filename = os.path.join(dir, 'index.html')
    print("Writing report to %r." % filename)
    r.to_html(filename, resources_dir=dir)

    data = {
            'Gnn': d.Gnn,
            'Gn': d.Gn,
            'G': d.G,
            'Q': d.Q,
            'Q_inv': d.Q_inv,
            'P_inv': d.P_inv
        }
    filename = os.path.join(options.outdir, 'tensors.pickle')
    print("Writing tensors to %r." % filename)
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def cov_plots(d):
    Q = d.Q
    Q_inv = d.Q_inv
    
    r = Report('cov')
    r.table('Q', Q)
    r.table('Q_inv', Q_inv)

    return r

def basic_plots(d):
    G = d.G
    #G = skim_top_and_bottom(G, 1)
    #max_value = numpy.abs(G).max()
    r = Report('plots')
    f = r.figure('The learned G', cols=2)
    cmd = {0: 'vx', 1: 'vy', 2: 'omega'}
    grad = {0: 'hor', 1: 'vert'}
    for (k, j) in itertools.product([0, 1, 2], [0, 1]):
        x = G[k, j, :, :].squeeze()
        #max_value = numpy.abs(G[k, ...]).max()
        n = r.data('G%d%d' % (k, j), x).display('posneg')
        f.sub(n, 'G %s %s' % (cmd[k], grad[j]))

    P = d.P
    f = r.figure('The covariance of gradient', cols=2)
    for (i, j) in itertools.product([0, 1], [0, 1]):
        x = P[i, j, :, :].squeeze()
        if i == j: x = scale_score(x)
        display = "scale" if i == j else "posneg"
        n = r.data('cov%d%d' % (i, j), x).display(display)
        f.sub(n, 'cov %s %s' % (grad[i], grad[j]))
    
    f = r.figure('The inverse of the covariance', cols=2)
    P_inv = d.P_inv
    #P_inv = skim_top_and_bottom(P_inv, 5)
    for (i, j) in itertools.product([0, 1], [0, 1]):
        x = P_inv[i, j, :, :].squeeze()
        if i == j: x = scale_score(x)
        display = "scale" if i == j else "posneg"
        n = r.data('P_inv%d%d' % (i, j), x).display(display)
        f.sub(n, 'P_inv %s %s' % (grad[i], grad[j]))
        
    Gn = d.Gn
    f = r.figure('Normalized G', cols=2)
    for (k, j) in itertools.product([0, 1, 2], [0, 1]):
        x = Gn[k, j, :, :].squeeze()
        n = r.data('Gn%d%d' % (k, j), x).display('posneg')
        f.sub(n, 'Gn %s %s' % (cmd[k], grad[j]))

    Gnn = d.Gnn
    #max_value = numpy.abs(Gnn).max()
    f = r.figure('Normalized G (also inputs)', cols=2)
    for (k, j) in itertools.product([0, 1, 2], [0, 1]):
        x = Gnn[k, j, :, :].squeeze()
        max_value = numpy.abs(Gnn[k, ...]).max()
        #max_value = numpy.abs(x).max()
        n = r.data('Gnn%d%d' % (k, j), x).display('posneg', max_value=max_value)
        f.sub(n, 'Gnn %s %s' % (cmd[k], grad[j]))


    plot_hist_for_4d_tensor(r, G, 'G', 'Histograms for G')
    plot_hist_for_4d_tensor(r, P, 'P', 'Histograms for P (covariance)')
    
    return r


def plot_hist_for_4d_tensor(report, T, id, caption):
    r = report.node(id)
    f = r.figure(caption=caption, cols=2)
    K = T.shape[0]
    N = T.shape[1]
    for (k, j) in itertools.product(range(K), range(N)):
        x = T[k, j, :, :].squeeze()
        nid = '%d%d' % (k, j)
        with r.data_pylab(nid) as pylab:
            pylab.hist(x.flat, bins=200)
        f.sub(nid)
    #report.add_child(r)

def get_information_matrix(P):
    # inverse for 2x2 matrix:
    #    1     | +d  -b |
    # -------  |        |
    # ad - bc  | -c   a |
    I = numpy.zeros(P.shape, 'float32')
    a = P[0, 0, :, :].squeeze()
    b = P[0, 1, :, :].squeeze()
    c = P[1, 0, :, :].squeeze()
    d = P[1, 1, :, :].squeeze()
    
    det = (a * d - b * c)
    det[det <= 0] = 1
    one_over_det = 1.0 / det
    
    I[0, 0, :, :] = one_over_det * (+d)
    I[0, 1, :, :] = one_over_det * (-b)
    I[1, 0, :, :] = one_over_det * (-c)
    I[1, 1, :, :] = one_over_det * (+a)
        
    return I

    
def normalize_G(G, P_inv):
    # matrix multiplication between the first two dimensions
    res = numpy.zeros(G.shape, 'float32')
    
    assert G.shape[0] == 3
    assert G.shape[1] == 2
    assert P_inv.shape[0] == 2
    assert P_inv.shape[1] == 2
    
    for i in [0, 1]:
        res[:, i, :, :] = (P_inv[i, 0, :, :] * G[:, 0, :, :] + 
                           P_inv[i, 1, :, :] * G[:, 1, :, :])
    return res

def normalize_input(G, Q_inv):
    assert Q_inv.shape[0] == Q_inv.shape[1]
    assert G.shape[0] == Q_inv.shape[0]
    # XXX: not sure
    Q_inv_sqrt = scipy.linalg.sqrtm(Q_inv)
    Q_inv_sqrt = Q_inv_sqrt.real()
    result = numpy.tensordot(Q_inv_sqrt, G, axes=(0, 0))
    assert result.shape == G.shape
    return result

def scale_score(x):
    y = x.copy()
    order = numpy.argsort(x.flat)
    # Black magic ;-) Probably the smartest thing I came up with today. 
    order_order = numpy.argsort(order)
    y.flat[:] = order_order.astype(y.dtype)
    return y


