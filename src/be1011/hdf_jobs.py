#!/usr/bin/env python
import os
from optparse import OptionParser
from collections import namedtuple

from compmake import comp, compmake_console, set_namespace
from procgraph import pg

import procgraph_rawseeds
import be1011 # XXX:

from .data_info import hdf_dir, logs

def convert_hdf2bpi(model, hdf, bpi, params):
    ''' Model: any procgraph model taking as config "hdf" and "file". '''
    if os.path.exists(bpi):
        print("Already done: %r exists." % bpi)
        return
        
    if not os.path.exists(hdf):
        raise Exception('File %r does not exist.' % hdf)
    
    tmp = bpi + '.part'
    if os.path.exists(tmp):
        print('Deleting previous temp file %r.' % tmp)
        os.unlink(tmp)
    
    # Update the config.
    config = dict(**params)
    config.update({'hdf': hdf, 'file': tmp})
    print("using %r" % config)
    # Actually run the model.
    pg(model, config)
    
    print("Renaming temporary file %r to %r." % (tmp, bpi))
    os.rename(tmp, bpi)
    
    
def main():
    set_namespace('hdf2bpi_all')
    
    parser = OptionParser()

    parser.add_option("--model", default=None,
                      help="Only do this model")
    
    (options, args) = parser.parse_args()
    
    if args:
        raise Exception('Extra arguments')
    
    
    Script = namedtuple('Script', 'job_prefix model input file_pattern params')
    
    scripts = [
        Script('3cams', 'rawseeds2bpi_3cams', '{logid}.h5', '{logid}.camera.bpi', {}),
        Script('4lasers', 'rawseeds2bpi_4lasers', '{logid}.h5', '{logid}.4lasers.bpi', {}),
        Script('frontal', 'rawseeds2bpi_frontal', '{logid}.h5', '{logid}.frontal.bpi', {}),
        Script('sick_extract', 'bpi_extract',
               '{logid}.4lasers.bpi', '{logid}.sick.bpi', {}),
        Script('sickpc', 'hdf_wrap_bpi_filter',
                '{logid}.sick.bpi', '{logid}.sickpc.bpi',
                {'bpi_filter': 'bpi_popcode',
                 'bpi_filter.edges': 'edges_sick.pickle' }),
        Script('sickpc_all', 'hdf_wrap_bpi_filter',
                '{logid}.sick.bpi', '{logid}.sickpca.bpi',
                {'bpi_filter': 'bpi_popcode',
                 'bpi_filter.edges': 'edges_sick-all.pickle' }),
    ]
    

    if not os.path.exists(hdf_dir):
        raise Exception('Input dir %r does not exist.' % hdf_dir)
    
    if not os.path.exists(hdf_dir):
        os.makedirs(hdf_dir)
    
    for log in logs:
        for script in scripts:
            hdf = os.path.join(hdf_dir, script.input.format(logid=log))
            bpi = os.path.join(hdf_dir, script.file_pattern.format(logid=log))
            job_id = '%s-%s' % (script.job_prefix, log)

            # if os.path.exists(bpi):
            #     print('File %r already exists; skipping creation of job %r.' %
            #             (bpi, job_id))
            #     continue
                
            comp(convert_hdf2bpi, script.model, hdf, bpi, script.params, job_id=job_id)
        
    compmake_console()

if __name__ == '__main__':
    main()




