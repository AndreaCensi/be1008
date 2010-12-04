import cPickle as pickle
from reprep import Report


def main():
    
    variables = 'smooth_random/variables.pickle.part'
    
    data = pickle.load(open(variables, 'rb'))
    
    R = data['correlation']
    
    
    r = Report('calibrator_plots')
    f = r.figure(cols=6)
    
    n = 100
    
    for i in range(n):
        id = 'sensel%d' % i
        Ri = R[i, :].reshape((100, 100))
        r.data(id, Ri)
        f.sub(id, display='posneg')
    
    filename = '%s.html' % r.id
    print("Writing to %r" % filename)
    r.to_html(filename)


if __name__ == '__main__':
    main()
