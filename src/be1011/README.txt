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
    
How to get the reduced problem: ::

    pg -m be1011 bpi_sample_random n=10000  bpi=${bpi}  file=${bpi}.10k
    
     

Calibrator simple tests
------------------------
    
    pg -m be1011 calibrator_test num_ref=100 bpi=${bpi}  file=cal_100.avi
    
    
    
     