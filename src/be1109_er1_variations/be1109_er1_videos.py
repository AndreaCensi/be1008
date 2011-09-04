from procgraph import pg, register_model_spec
import os
from optparse import OptionParser

def main():
    usage = ''
    
    parser = OptionParser(usage=usage)
    
    parser.add_option("--base", default='.', help="Base directory")
    
    parser.add_option("--out", help="Destination base directory")
    
    (options, args) = parser.parse_args()
    
    for logdir in  dirs:
        logname = os.path.basename(logdir)
        outdir = os.path.join(options.out, logname)
        done_file = os.path.join(outdir, 'finished.txt')
        if os.path.exists(done_file):
            print('Skipping %r' % logdir)
            continue

        try:
            pg('er1convert', dict(logdir=logdir, outdir=outdir))

            with open(done_file, 'w') as f:
                f.write('done :-)\n')
        except Exception as e:
            print e
            continue

def file_creation_job(input_file, output_file, function_to_call):
    if os.path.exists(output_file):
        print('File %r already exists', output_file)
        return

    function_to_call()
    
    if not os.path.exists(output_file):
        msg = ('File %r not created.' % output_file)
        raise Exception(msg)

if __name__ == '__main__':
    main()
    








