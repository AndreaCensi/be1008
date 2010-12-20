import os
import cPickle as pickle
from optparse import OptionParser
from be1011.calibrator_plots import OpenStruct
from reprep import Report
import itertools
from procgraph_images.copied_from_reprep import skim_top_and_bottom
import numpy

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
    
    r = Report('boot')
    
    r.add_child(basic_plots(d))
    
    dir = os.path.join(options.outdir, 'plots')
    filename = os.path.join(dir, 'index.html')
    print("Writing to %r." % filename)
    r.to_html(filename, resources_dir=dir)

def basic_plots(d):
    G = d.G
    #G = skim_top_and_bottom(G, 1)
    max_value = numpy.abs(G).max()
    r = Report('plots')
    f = r.figure('The learned G', cols=2)
    cmd = {0: 'vx', 2: 'omega'}
    grad = {0: 'hor', 1: 'vert'}
    for (k, j) in itertools.product([0, 2], [0, 1]):
        x = G[k, j, :, :].squeeze()
        n = r.data('G%d%d' % (k, j), x).display('posneg')
        f.sub(n, 'G %s %s' % (cmd[k], grad[j]))

    P = d.P
    f = r.figure('The covariance of gradient', cols=2)
    for (i, j) in itertools.product([0, 1], [0, 1]):
        x = P[i, j, :, :].squeeze()
        display = "scale" if i == j else "posneg"
        n = r.data('cov%d%d' % (i, j), x).display(display)
        f.sub(n, 'cov %s %s' % (grad[i], grad[j]))
    
    f = r.figure('The inverse of the covariance', cols=2)
    P_inv = d.P_inv
    #P_inv = skim_top_and_bottom(P_inv, 5)
    for (i, j) in itertools.product([0, 1], [0, 1]):
        x = P_inv[i, j, :, :].squeeze()
        x = skim_top_and_bottom(x, 2)
        display = "scale" if i == j else "posneg"
        n = r.data('P_inv%d%d' % (i, j), x).display(display)
        f.sub(n, 'P_inv %s %s' % (grad[i], grad[j]))
        
    Gn = d.Gn
    f = r.figure('Normalized G', cols=2)
    for (k, j) in itertools.product([0, 2], [0, 1]):
        max_value = numpy.abs(Gn[k, ...]).max()
        x = Gn[k, j, :, :].squeeze()
        max_value = numpy.abs(x).max()
        x = skim_top_and_bottom(x, 0.2)
        n = r.data('Gn%d%d' % (k, j), x).display('posneg', max_value=max_value)
        f.sub(n, 'Gn %s %s' % (cmd[k], grad[j]))

    return r


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
    
    #P_inv[0, 1, ...] = 0
    #P_inv[1, 0, ...] = 0
    
    for i in [0, 1]:
        res[:, i, :, :] = (P_inv[i, 0, :, :] * G[:, 0, :, :] + 
                           P_inv[i, 1, :, :] * G[:, 1, :, :])
    return res
    
    
    
    
    
    
    


