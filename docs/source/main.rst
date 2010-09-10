Notes 
======


These are some personal notes how all of this works. 


1. Run ``be_all``. It expects to be run in the base directory of rawseeds ::

	$ ls
    Bicocca_2009-02-25a/ 
	Bicocca_2009-02-26a/ 
	...
	$ be_all

You cannot run the *predict jobs as they need the tensor fields as described below.

The output goes into a subdirectory of the log directories. The convention is: ::

    Bicocca_2009-02-25a/out/<experiment>/<configuration>/file 

Moreover, there are "memory" files created by :ref:`block:memories`.


2. Run the average operations that create the data:

	# creates laser_bgds_boot.pickle
	$ be_average_logs_results --dir . --experiment laser_bgds_boot

	# reads laser_bgds_boot.pickle, creates
	#     out/laser_bgds_boot.html (reprep report)
	#     out/laser_bgds_boot/<variant>:GB.pickle    <-- contains the tensors to use
    $ be_laser_bgds_boot_display

Then run ``be_all`` again with the ``*predict`` jobs.

For the camera, the operations are similar:

	$ be_average_logs_results --dir . --experiment camera_bgds_boot
	$ be_average_logs_results --dir . --experiment camera_bgds_stats
	$ be_camera_bgds_boot_display
	$ be_memories_display
	
	$ be_camera_figures


Indices and tables
==================

.. toctree::
   :maxdepth: 2

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

