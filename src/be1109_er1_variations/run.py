from compmake import comp, compmake_console
from optparse import OptionParser
from procgraph import pg
import itertools
import os
from procgraph.block_utils.file_io import make_sure_dir_exists

def list_logdirs(D):
    l = []
    for d in os.listdir(D):
        if len(d) == len('20100604_194126'): #
            l.append(os.path.join(D, d))
    return l

def main():
    usage = ''
    
    parser = OptionParser(usage=usage)
    
    parser.add_option("--bigdata", default="~/BIGDATA", help="Base directory")
    
    parser.add_option("--outdir", help="Destination base directory")
    
    (options, args) = parser.parse_args()
    if args:
        raise Exception('trailing')

    if options.outdir is None:
        raise Exception('Specify outdir')
    
    bigdata = os.path.expanduser(options.bigdata)
    bigdata = os.path.expandvars(bigdata)
    
    conf2logs = {}
    conf2logs['conf1b'] = list_logdirs(os.path.join(bigdata, "er1-logs_compact_better", "conf1"))
    conf2logs['conf2b'] = list_logdirs(os.path.join(bigdata, "er1-logs_compact_better", "conf2"))
    conf2logs['conf0b'] = conf2logs['conf1b'] + conf2logs['conf2b']
    # what to run
    # interface is   {logdir, logname, outdir}
    conf2pg = {} 
    conf2pg['conf0b'] = ['er1b_video0', 'er1conv_video0_bw_full',
                         'er1conv_video0_bw_small']
    conf2pg['conf1b'] = ['er1b_video01',
                         'er1conv_video0_bw_full',
                         'er1conv_video0_bw_small',
                         'er1conv_video01_bw_full',
                         'er1conv_video01_bw_small']
    conf2pg['conf2b'] = conf2pg['conf1b']
    
    for conf in conf2pg:
        logs = conf2logs[conf]
        pgs = conf2pg[conf]
        
        for logdir, pg in itertools.product(logs, pgs): #@UndefinedVariable
            logname = os.path.basename(logdir)
            outdir = os.path.join(options.outdir, conf) 
            
            job_id = '%s-%s-%s' % (conf, pg, logname)
            done_file = os.path.join(options.outdir, 'done', '%s-finished.txt' % job_id)
            make_sure_dir_exists(done_file)
            
            config = dict(logdir=logdir, outdir=outdir, logname=logname)
            comp(run_pg_script, pg, config, done_file, job_id=job_id)

    compmake_console()


def run_pg_script(model, model_config, done_file):
    if os.path.exists(done_file):
        return
    pg(model, model_config)

    with open(done_file, 'w') as f:
        f.write('done :-)\n')

#
#def file_creation_job(input_file, output_file, function_to_call):
#    if os.path.exists(output_file):
#        print('File %r already exists', output_file)
#        return
#
#    function_to_call()
#    
#    if not os.path.exists(output_file):
#        msg = ('File %r not created.' % output_file)
#        raise Exception(msg)

if __name__ == '__main__':
    main()
    








