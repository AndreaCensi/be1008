from setuptools import setup, find_packages


setup(
    name='be1008',
    author="Andrea Censi",
    author_email="andrea@cds.caltech.edu",
    version="1.0",
    package_dir={'':'src'},
    packages=find_packages('src'),
    entry_points={
     'console_scripts': [
       'be_average_logs_results     = be1008.average_logs_results:main',
       'be_camera_bgds_boot_display = be1008.camera_bgds_boot_display:main',
       'be_laser_bgds_boot_display  = be1008.laser_bgds_boot_display:main',
       'be_all                      = be1008.be_all:main',
       'be_memories_display         = be1008.memories_display:main',
       'be_materials                = be1008.be_materials:main',
       'be_materials2               = be1008.be_materials2:main',
       'be_camera_figures           = be1008.camera_figure:main',
       
       'generic_bgds_boot_plots     = be1011.generic_bgds_boot_plots:main',
       'calib_1D_stats_plots        = be1011.calib_1D_stats_plots:main',
       'compute_percentiles         = be1011.compute_percentiles:main',
       'hdf_jobs                    = be1011.hdf_jobs:main',
       'calib_main  =                 be1011.calib_main:main',
       
       'be1103_er1_convert = be1103_importing.er1_convert:main',

       'bv_generate_simulated       = be1102.generate_simulated:main',
       
       ]
       },
    install_requires=[],
    extras_require={},
    include_package_data=True,
    package_data={
        'be1008': ['models/*.pg', '*.pg']
    }
)

