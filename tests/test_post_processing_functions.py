from copy import deepcopy

# import REC input and output data
from rec_sizing.optimization.structures.I_O_collective_pool_milp_postprocessing import (
    INPUTS_INSTALL_POOL_PP,
    INPUTS_OWNERSHIP_PP,
    OUTPUTS_INSTALL_POOL_PP
)

# import optimization and post-processing module
from rec_sizing.optimization_functions import *
from rec_sizing.post_processing_functions import *


def test_collective_pool_milp_postprocessing():
    """optimization"""
    results = run_pre_collective_pool_milp(INPUTS_INSTALL_POOL_PP)
    # post-processing
    results_pp = run_post_processing(results, INPUTS_INSTALL_POOL_PP, INPUTS_OWNERSHIP_PP)

    for ki, valu in results_pp.items():
        assert valu == OUTPUTS_INSTALL_POOL_PP.get(ki), f'{ki}'


if __name__ == '__main__':
    test_collective_pool_milp_postprocessing()
