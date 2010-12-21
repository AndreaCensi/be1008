import os
import numpy.linalg
import itertools
import cPickle as pickle
from reprep import Report
from optparse import OptionParser

from .random_extract import RandomExtract
from .fast_kendall_tau import fast_kendall_tau


def main():    
    parser = OptionParser()
    
    parser.add_option("--outdir",
                  type="string", help='Directory containing data')

    (options, args) = parser.parse_args() #@UnusedVariable
    assert not args
    
    variables = os.path.join(options.outdir, 'variables.pickle.part')
    
    data = pickle.load(open(variables, 'rb'))
    
    d = OpenStruct(**data)
    d.R = d.correlation
    d.num_ref, d.num_sensels = d.R.shape
    assert d.num_ref <= d.num_sensels
    d.imshape = (100, 100) # XXX
    d.toimg = lambda x : x.reshape(d.imshape)
    
    r = Report('calibrator_analysis')
    
    r.add_child(new_analysis(data))
    r.add_child(correlation_embedding_report(R=data['correlation'], num_eig=6)) 
    r.add_child(show_some_correlations(d, num=20))
    
    filename = os.path.join(options.outdir, 'supersensels.html')
    print("Writing to %r" % filename)
    r.to_html(filename)


def new_analysis(data, nclasses=100):
    R = data['correlation']
    num_ref, num_sensels = R.shape
    assert num_ref <= num_sensels
    
    # variance = data['variance']
    
     
    classes = group_by_correlation(R[:nclasses, :])
    
    nclasses = classes.max() + 1
    
    assert (classes >= 0).all()
    assert (classes < nclasses).all()
    
     
    
    print("Computing class correlation...")
    classes_correlation = numpy.zeros((nclasses, nclasses))
    for c1, c2 in itertools.product(range(nclasses), range(nclasses)):
        if c1 < c2:
            continue
        
        # If I had the full matrix
        #sensels1, = numpy.nonzero(classes == c1)
        #sensels2, = numpy.nonzero(classes == c2)
        #average_correlation = R[sensels1,sensels2].mean()
        
        corr1 = R[c1, :]
        corr2 = R[c2, :]
        assert len(corr1) == len(corr2) == num_sensels 
        
        # similarity = (corr1 * corr2).mean() 
        # similarity = (corr1 * corr2).mean() / (corr1.mean() * corr2.mean())
        
        corr1 = corr1 / numpy.linalg.norm(corr1)
        corr2 = corr2 / numpy.linalg.norm(corr2)
        similarity = numpy.linalg.norm(corr1 - corr2)
        
        classes_correlation[c1, c2] = similarity
        classes_correlation[c2, c1] = similarity
    
    print("Computing class correlation...")
    U, S, V = numpy.linalg.svd(classes_correlation, full_matrices=0)
    
    # FIXME: U or V?
    
    # XXX: should I use this?
    classes_coords = U / numpy.sqrt(S)
    
    
    print("Creating report...")
    r = Report('new_analysis')
    f0 = r.figure(caption='Summary')
    imshape = (100, 100) # XXX
    toimg = lambda x : x.reshape(imshape)
    
    f0.sub(r.data('supers', toimg(classes)).display('scale'))

    f0.sub(r.data('classes_correlation', classes_correlation).display('scale'))

    f = r.figure('eigen_v', cols=3)
    for k in range(6):
        coord = V[k, :] / numpy.sqrt(S)
        assert coord.size == nclasses
        coordi = coord[classes]
        assert coordi.size == num_sensels
        n = r.data('coord%d' % k, toimg(coordi)).display('posneg')
        f.sub(n)
    
    f = r.figure('eigen_u', cols=3)
    for k in range(6):
        coord = U[:, k] / numpy.sqrt(S)
        assert coord.size == nclasses
        coordi = coord[classes]
        assert coordi.size == num_sensels
        n = r.data('coordu%d' % k, toimg(coordi)).display('posneg')
        f.sub(n)
    
    return r
    
def group_by_correlation(R):
    num_ref, num_sensels = R.shape
    assert num_ref <= num_sensels
    classes = numpy.zeros((num_sensels,), dtype='int32')
    for i in range(num_sensels):
        classes[i] = numpy.argmax(R[:, i])
    return classes

    
def correlation_embedding_report(R, num_eig=6):
    imshape = (100, 100)
    toimg = lambda x : x.reshape(imshape)
    
    U, S, V = numpy.linalg.svd(R, full_matrices=0) #@UnusedVariable
    
    r = Report('correlation_embedding')
    fv = r.figure('V', caption='Coordinates of the embedding')
    
    for k in range(num_eig):
        v = V[k, :] * numpy.sqrt(S[k])
        print v.size
        id = 'eig_v_%d' % k
        n = r.data(id, toimg(v)).display('posneg')
        fv.sub(n, caption='Eigenvector #%d' % k)
    
    return r

def show_some_correlations(d, num=30, cols=6):
    r = Report('sensels correlations')
    f = r.figure('Correlations of some sensels.', cols=cols)
    
    s = d.R.sum(axis=0)
    r.data('sum', d.toimg(s)).display('posneg')
    f.sub('sum', caption="Sum of correlations")
    
    for i in range(num):
        id = 'sensel%d' % i
        Ri = d.toimg(d.R[i, :])
        r.data(id, Ri).display('posneg')
        f.sub(id)
    return r
        
def old_analysis(data):
    R = data['correlation']
    variance = data['variance']
    num_sensels = max(R.shape)
    # XXX
    imshape = (100, 100)
    num_coords_keep = 10
    
    num_sensels_display = 100
    
    r = Report('calibrator_plots')
    f0 = r.figure(cols=5, caption='Main quantities')
    f1 = r.figure(cols=6)
    f2 = r.figure(cols=6)
    f3 = r.figure(cols=6, caption='distances in sensing space')
    f4 = r.figure(cols=6, caption='dependency between eigenvectors')
    
    f0.sub(r.data('variance', variance.reshape(imshape)).display('scale', min_value=0),
           caption='Variance (darker=stronger)')

    
    with r.data_pylab('variance_scalar') as pylab:
        pylab.hist(variance)
    f0.sub('variance_scalar')
    
    for i in range(num_sensels_display):
        id = 'sensel%d' % i
        Ri = R[i, :].reshape(imshape)
        r.data(id, Ri)
        f1.sub(id, display='posneg')
    
    U, S, V = numpy.linalg.svd(R, full_matrices=0) #@UnusedVariable
     
    
    
    coords = numpy.zeros(shape=(num_sensels, num_coords_keep))
    # set coordinates
    for k in range(num_coords_keep):
        v = V[k, :] * numpy.sqrt(S[k])
        coords[:, k] = v
        
    # normalize coords
    if False:
        for i in range(num_sensels):
            coords[i, :] = coords[i, :] / numpy.linalg.norm(coords)
            
    for k in range(num_coords_keep):
        id = 'coord%d' % k
        M = coords[:, k].reshape(imshape)
        r.data(id, M)
        f2.sub(id, display='posneg')
    
    # compute the distance on the sphere for some sensel

    for w in  RandomExtract.choose_selection(30, num_sensels):
        D = numpy.zeros(num_sensels)
        s = 14 # number of coordinates
        p1 = coords[w, 0:s] / numpy.linalg.norm(coords[w, 0:s])
        for i in range(num_sensels):
            p2 = coords[i, 0:s] / numpy.linalg.norm(coords[i, 0:s])
            D[i] = numpy.linalg.norm(p1 - p2)
            
        D_sorted = numpy.argsort(D)
        neighbors = 50
        D[D_sorted[:neighbors]] = 0
        D[D_sorted[neighbors:]] = 1
        # D= D_sorted
        id = 'dist%s' % w
        r.data(id, D.reshape(imshape))
        f3.sub(id, display='scale')
    
    # Divide the sensels in classes
    if False:
        ncoords_classes = 5
        classes = numpy.zeros((num_sensels))
        for k in range(ncoords_classes):
            c = coords[:, k]
            cs = divide_in_classes(c, 3) 
            classes += cs * (3 ** k)
        
        f0.sub(r.data('classes', classes.reshape(imshape)).display('posneg'))
    if True:
        nclasses = 20
        classes = group_by_correlation(R[:nclasses, :])
        f0.sub(r.data('classes_by_R', classes.reshape(imshape)).display('scale'))
        
    if False:
        ncoords = 10
        print("computing similarity matrix")
        coord_similarity = numpy.zeros((ncoords, ncoords))
        for k1, k2 in itertools.product(range(ncoords), range(ncoords)):
            if k1 == k2:
                coord_similarity[k1, k2] = 0 # numpy.nan
                continue
            if k1 < k2:
                continue
            
            c1 = coords[:, k1]
            c2 = coords[:, k2]
            step = 4
            c1 = c1[::step]
            c2 = c2[::step]
            tau, prob = fast_kendall_tau(c1, c2)
            
            coord_similarity[k1, k2] = numpy.abs(tau)
            coord_similarity[k2, k1] = coord_similarity[k1, k2]
        
            print('%r %r : tau = %.4f  prob = %.4f' % (k1, k2, tau, prob))
        print coord_similarity.__repr__()
        n = r.data('coord_similarity', coord_similarity).display('posneg')
        f4.sub(n)
            
        with r.data_pylab('sim_score') as pylab:
            pylab.plot(coord_similarity.sum(axis=0), 'x-')
            pylab.xlabel('coordinate')
            pylab.ylabel('total similarity')
        f4.sub('sim_score')
        
        with r.data_pylab('comp0') as pylab:
            pylab.plot(coord_similarity[0, :], 'x-')
            pylab.xlabel('coordinate')
            pylab.ylabel('similarity with #0')
        f4.sub('comp0')
        
        ref = 0
        for k in range(10):
            print "comparison", k
            id = 'cmp_%d_%d' % (ref, k)
            c0 = coords[:, ref]
            ck = coords[:, k]
            with r.data_pylab(id) as pylab:
                pylab.plot(c0, ck, '.', markersize=0.3)
    
            f4.sub(id)
    return r

def divide_in_classes(x, nclasses):
    print "sorting"
    sorted = numpy.argsort(x)
    print "done"
    results = numpy.zeros(x.shape)
    results[:] = -1
    for c in range(nclasses):
        low = numpy.floor(c * (1.0 / nclasses) * x.size)
        high = numpy.floor((c + 1) * (1.0 / nclasses) * x.size)
        sensels_in_class = sorted[low:high]
        print '%d %d:%d' % (c, low, high)
        results[sensels_in_class] = c
    
    assert (results >= 0).all()
    return results

    
class OpenStruct:
    def __init__(self, **dic):
        self.__dict__.update(dic)
    def __getattr__(self, i):
        if i in self.__dict__:
            return self.__dict__[i]
        else:
            raise AttributeError, i
    def __setattr__(self, i, v):
        if i in self.__dict__:
            self.__dict__[i] = v
        else:
            self.__dict__.update({i:v})
        return v # i like cascates :)
   

if __name__ == '__main__':
    main()
    
