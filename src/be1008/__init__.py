''' Bootstrapping experiments '''
from procgraph import pg_add_this_package_models
 

import predictor
import bgds_1d_predictor 
import memories


pg_add_this_package_models(file=__file__, assign_to=__package__)