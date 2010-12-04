import cPickle as pickle
from reprep import Report
from optparse import OptionParser
import os
import numpy.linalg
from be1011.random_extract import RandomExtract


def main():
    
    parser = OptionParser()
    
    parser.add_option("--outdir",
                  type="string", help='Directory containing data')

    (options, args) = parser.parse_args() #@UnusedVariable
    assert not args
    
    variables = os.path.join(options.outdir, 'variables.pickle.part')
    
    data = pickle.load(open(variables, 'rb'))
    
    R = data['correlation']
    num_sensels = max(R.shape)
    
    r = Report('calibrator_plots')
    f1 = r.figure(cols=6)
    f2 = r.figure(cols=6)
    f3 = r.figure(cols=6, caption='distances in sensing space')
    
    n = 100
    imshape = (100, 100)
    for i in range(n):
        id = 'sensel%d' % i
        Ri = R[i, :].reshape((100, 100))
        r.data(id, Ri)
        f1.sub(id, display='posneg')
    
    U, S, V = numpy.linalg.svd(R, full_matrices=0) #@UnusedVariable
     
    K = 100
    coords = numpy.zeros(shape=(num_sensels, K))
    for k in range(K):
        id = 'eig%d' % k
        v = V[k, :] * numpy.sqrt(S[k])
        coords[:, k] = v
        M = v.reshape((100, 100))
        r.data(id, M)
        f2.sub(id, display='posneg')
    
    # compute the distance on the sphere for one sensel

    for w in  RandomExtract.choose_selection(30, num_sensels):
        D = numpy.zeros(num_sensels)
        for i in range(num_sensels):
            s = 14
            D[i] = numpy.linalg.norm(coords[w, 0:s] - coords[i, 0:s])
        id = 'dist%s' % w
        r.data(id, D.reshape(imshape))
        f3.sub(id, display='scale')
    
    filename = os.path.join(options.outdir, '%s.html' % r.id)
    print("Writing to %r" % filename)
    r.to_html(filename)


if __name__ == '__main__':
    main()
