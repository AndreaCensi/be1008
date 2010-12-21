#!/usr/bin/env python
import os
from compmake import comp, compmake_console, set_namespace
from procgraph import pg

import procgraph_rawseeds #@UnusedImport

from data_info import hdf_dir, logs, rawseeds_dir

def convert_rawseeds2hdf(logdir, hdf):
    if os.path.exists(hdf):
        print("Already done: %r exists." % hdf)
        return

    if not os.path.exists(logdir):
        raise Exception('Logdir %r does not exist.' % logdir)
    
    tmp = hdf + '.part'
    if os.path.exists(tmp):
        print('Deleting previous temp file %r.' % tmp)
        os.unlink(tmp)
        
    pg('rawseeds2hdf', {'logdir': logdir, 'file': tmp})
    
    print("Renaming temporary file %r to %r." % (tmp, hdf))
    os.rename(tmp, hdf)
    
def main():
    set_namespace('rawseeds2hdf')

    if not os.path.exists(rawseeds_dir):
        raise Exception('Input dir %r does not exist.' % hdf_dir)
    
    if not os.path.exists(hdf_dir):
        os.makedirs(hdf_dir)
    
    for log in logs:
        logdir = os.path.join(rawseeds_dir, log)
        hdf = os.path.join(hdf_dir, '%s.h5' % log)
        job_id = 'rawseeds2hdf-%s' % log
        comp(convert_rawseeds2hdf, logdir, hdf, job_id=job_id)
        
    compmake_console()

if __name__ == '__main__':
    main()




