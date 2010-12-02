

bpi=Bicocca_2009-02-25a.h5.part.bpi

alias cmd='pg -m be1011 random_sensel_video bpi=${bpi}'

pg -m be1011 random_sensel_video bpi=${bpi} n=64 sensel_cols=8 out=sensels_64.avi
pg -m be1011 random_sensel_video bpi=${bpi} n=1024 sensel_cols=32 out=sensels_1k.avi
pg -m be1011 random_sensel_video bpi=${bpi} n=10000 sensel_cols=100 out=sensels_10k.avi
