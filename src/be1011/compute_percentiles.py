from optparse import OptionParser
import tables
import numpy
import pickle

def main():
    parser = OptionParser()
    parser.add_option("--log", help='HDF file containing table procgraph/y')
    parser.add_option("--output", help='pickle file with output')
    (options, args) = parser.parse_args() #@UnusedVariable

    h5 = tables.openFile(options.log)
    y = h5.root.procgraph.y[:]['value']

    N = 100
    percs = numpy.linspace(0, 100, N)
    
    edges = numpy.percentile(y.flat, list(percs))
    
    edges = numpy.unique(edges)
    print 'Found %d edges.' % len(edges)
    print list(edges)
    
    h5.close()
    
    print('Writing on file %r.' % options.output)
    with open(options.output, 'wb') as f:
        pickle.dump(list(edges), f)

#y = h5.root.procgraph.y[:]['value']
#y_sick = h5.root.procgraph.y[:]['value'][:, 0:362]
#y_hok = h5.root.procgraph.y[:]['value'][:, 362:]
