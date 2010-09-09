
from compmake import comp, compmake_console
from procgraph.scripts.pg import pg

import procgraph_rawseeds #@UnusedImport

scripts = """
rawseeds_camera_display
rawseeds_camera_display_contrast
rawseeds_laser_display
rawseeds_camera_mean
rawseeds_camera_mean_contrast
rawseeds_camera_var
rawseeds_camera_var_contrast
rawseeds_laser_bgds_boot_all
rawseeds_laser_bds_boot
rawseeds_laser_corr
rawseeds_camera_bgds_boot_all
rawseeds_camera_bgds_stats_all
rawseeds_camera_bgds_predict_all
rawseeds_laser_bgds_predict_all
""".split()

# removed: rawseeds_big_movie


logs = """
Bicocca_2009-02-25a
Bicocca_2009-02-25b
Bicocca_2009-02-26a
Bicocca_2009-02-26b
Bicocca_2009-02-27a
Bovisa_2008-09-01
Bovisa_2008-10-04
Bovisa_2008-10-06
Bovisa_2008-10-07
Bovisa_2008-10-11a
Bovisa_2008-10-11b
""".split()

def be_all():
    for log in logs:
        for script in scripts:
            job_id = '%s-%s' % (script, log)
            #config = {'logdir': "${PBENV_DATA}/rawseeds/%s" % log}
            config = {'logdir':  log}
            comp(pg, script, config=config, job_id=job_id)

    compmake_console()

if __name__ == '__main__':
    be_all()
    
