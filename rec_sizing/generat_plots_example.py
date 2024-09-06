import os
import pickle

# import REC input and output data
from rec_sizing.optimization.structures.I_O_collective_pool_milp_postprocessing import (
    INPUTS_INSTALL_POOL_PP,
    INPUTS_OWNERSHIP_PP
)

# import optimization and post-processing module
from rec_sizing.optimization_functions import *
from rec_sizing.post_processing_functions import *

# import generate_plots functions
from rec_sizing.generate_plots import *

'''Init Test'''
# establishes the name of the running test to save outputs
test_name = 'test_description'
outputs_dir = os.getcwd() + '\\outputs\\' + test_name + '\\'
if not os.path.exists(outputs_dir): os.makedirs(outputs_dir)

'optimization'
results = run_pre_collective_pool_milp(INPUTS_INSTALL_POOL_PP)
'post-processing'
results_pp = run_post_processing(results, INPUTS_INSTALL_POOL_PP, INPUTS_OWNERSHIP_PP)

'''### plots ###'''
# optimization plots per installation
plot_results_optimization(results_pp, INPUTS_INSTALL_POOL_PP, outputs_dir)
# post-processing costs per installation: OF desegregated; Internal market compensations
plot_results_installationCosts(results_pp, outputs_dir)
# post-processing costs per member with Internal market compensations
plot_results_membersCosts(results_pp, outputs_dir)

with open(outputs_dir + test_name + '.pickle', 'wb') as handle:
    # pickle.dump(INPUTS_INSTALL_POOL, handle)
    pickle.dump(results_pp, handle)
