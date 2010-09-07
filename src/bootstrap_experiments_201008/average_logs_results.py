from optparse import OptionParser
import os
import re
import pickle
import numpy

def average_logs_results():
    
    usage = "Example usage: %prog --dir .   --pattern  B*/*/*.pickle" \
            """ We assume that the path is like:
            
                <dir>/<log>/out/<experiment>/<variant>/<data>.pickle
                
            """
    parser = OptionParser(usage=usage)
     
    parser.add_option("--dir", default=".",
                      help="Directory where logs are stored.")
    parser.add_option("--experiment", default="camera_bgds_boot",
                      help="Experiment to consider")
    parser.add_option("--output", default=None)

#    parser.add_option("--pattern", default=" B*/**/*.pickle",
#                      help="Pattern for the act where logs are stored.")
    (options, args) = parser.parse_args() #@UnusedVariable
    
    #pattern = r"\A(?P<log>[\w\-\d]+)/.+/(?P<data>\w+)\.pickle\Z"
    
    pattern = re.compile(r"""
 \A                  # match from beginning of the string
 (?P<log>[\w\-\d]+)  # We first meet the log name
 /out/               # skip a /
 %s                  # here we fill in the experiment name
 /                   # skip a /
 (?P<variant>[\w\-\d/]+) # the variant of the experiment
 /
 (?P<data>\w+)       # finally the data
 \.pickle            # don't include extension
 \Z                  # match to the end of the string
""" % options.experiment, re.VERBOSE)

    variants = {}
    
    for dirpath, dirnames, files in os.walk(options.dir): #@UnusedVariable
        print "Considering %s" % dirpath
        for f in files:
            complete = os.path.join(dirpath, f)
            relative = os.path.relpath(complete, options.dir)
            m = re.match(pattern, relative)
            if m: 
                variant = m.group('variant')
                data = m.group('data')
                log = m.group('log')
                
                if not variant in variants:
                    variants[variant] = {}
                
                if not data in variants[variant]:
                    variants[variant][data] = []
                    
                variants[variant][data].append(complete)

        avoid = ['OMNI', 'FRONTAL', 'SVS_T', 'SVS_R', 'SVS_L']
        for a in avoid:
            if a in dirnames:
                dirnames.remove(a)


    results = {}
    
    for variant, variant_data in variants.items():
        results[variant] = {}
        for variable, files in variant_data.items():
            print 'Reading %d files for %s / %s' % (len(files), variant, variable)
            datas = map(lambda x: pickle.load(open(x, 'rb')), files)
            average = numpy.mean(datas, axis=0)
            results[variant][variable] = average

    output = options.output
    if output is None:
        output = "%s.pickle" % options.experiment
    print "Writing results to %s" % output
    pickle.dump(results, open(output, 'wb'))

if __name__ == '__main__':
    average_logs_results()
