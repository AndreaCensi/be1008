from setuptools import setup, find_packages


setup(
    name='bootstrap_experiments_201008',
    author="Andrea Censi",
    author_email="andrea@cds.caltech.edu",
    version="0.1",
    package_dir={'':'src'},
    packages=['bootstrap_experiments_201008'],
    entry_points={
     'console_scripts': [
       'average_logs_results = '
        'bootstrap_experiments_201008.average_logs_results:average_logs_results',
       'camera_bgds_boot_display = '
        'bootstrap_experiments_201008.camera_bgds_boot_display:camera_bgds_boot_display'
       ]
       },
    install_requires=[],
    extras_require={
    #'multiprocessing':  ['redis']
    # TODO: learn how to use this feature
    # TODO: add gvgen
    },
    include_package_data=True,
    package_data={
        'bootstrap_experiments_201008': ['models/*.pg', '*.pg']
    }
)

