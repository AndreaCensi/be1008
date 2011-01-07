How to create some of the sensels videos
----------------------------------------

Example script: ::

    bpi=Bicocca_2009-02-25a.h5.part.bpi

    alias cmd='pg -m be1011 random_sensel_video bpi=${bpi}'

    pg -m be1011 random_sensel_video bpi=${bpi} n=64 sensel_cols=8 out=sensels_64.avi
    pg -m be1011 random_sensel_video bpi=${bpi} n=1024 sensel_cols=32 out=sensels_1k.avi
    pg -m be1011 random_sensel_video bpi=${bpi} n=10000 sensel_cols=100 out=sensels_10k.avi

Reducing
--------
    
How to get the reduced problem with random pixels: ::

    pg -m be1011 bpi_sample_random n=10000  bpi=${bpi}  file=${bpi}.10k
    

Calibrator simple tests
------------------------
    
    pg -m be1011 calibrator_test demo.num_ref=100 bpi=${bpi}  outdir=results/
    
How to repack a bpi without compression for random access: 
 
    ptrepack --shuffle=0 --complevel=0 --fletcher32=0 ${bpi} ordered.bpi
 
How to preprocess y_dot (smoothing):
 
    pg -m be1011 preprocess_ydot bpi=${bpi}  file=y_dot_smooth.bpi


Calibrator 1d tests (sick)
--------------------------

pg -m be1011 calib_1D_stats \
             edges=edges_sick-16.pickle \
             files="${PBENV_DATA}/rawseeds_hdf/*.sick.bpi" \
             output=calib_sick/calib_1D_stats3.pickle

# Old processing:
# calib_1D_stats_plots --outdir calib_sick --file calib_sick/calib_1D_stats.pickle


Testing the population code logic
---------------------------------

bpi=rawseeds_hdf/Bovisa_2008-09-01.4lasers.bpi
pg -m be1011 pop_code_tests bpi=${bpi} edges=edges_sick.pickle file=out.avi


Computing the population code files
-----------------------------------

Concatenate the files together:

    pg -m be1011 bpi_y_cat \
                 files="${PBENV_DATA}/rawseeds_hdf/*.sick.bpi" \
                 output=rawseeds_hdf/sick-all.h5

Compute the percentiles:

    compute_percentiles --log rawseeds_hdf/sick-all.h5 --output edges_sick-all.pickle

    compute_percentiles --bins 16 --log rawseeds_hdf/sick-all.h5 --output edges_sick-16.pickle

Running BGDS boot from bpi
--------------------------

Single file:

    pg -m be1011 bpi_bgds_boot \
             bpi="${PBENV_DATA}/rawseeds_hdf/Bovisa_2008-09-01.sickpc.bpi" 
             outdir='tmp'

Multiple files:

    pg -m be1011 bpi_bgds_boot_many \
        files="${PBENV_DATA}/rawseeds_hdf/*.sickpca.bpi" \
        outdir='boot_sickpca/'

1d:

pg -m be1011 bpi_bgds_boot_many \
        files="${PBENV_DATA}/rawseeds_hdf/*.sick.bpi" \
        outdir='boot_sick1d/'


Plotting and generating normalized tensors:

    generic_bgds_boot_plots --outdir boot_sickpc

This writes outdir/tensors.pickle.

Run predictor for sick/PC:

pg -m be1011 bpi_bgds_predict_sick  log=Bicocca_2009-02-26a  outdir='boot_sickpca/'
    
    
    
    # pg -m be1011 bpi_bgds_predict  bpi="${PBENV_DATA}/rawseeds_hdf/Bovisa_2008-09-01.sickpca.bpi" outdir='boot_sickpca/'
     
     