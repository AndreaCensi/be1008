#import predictor
import os


# FIXME, make this easier
from procgraph.core.registrar import default_library
from procgraph.core.model_loader import pg_look_for_models
dir = os.path.join(os.path.dirname(__file__), 'models')
pg_look_for_models(default_library, additional_paths=[dir], ignore_env=True,
                   assign_to_module='bootstrap_experiments_201008')



