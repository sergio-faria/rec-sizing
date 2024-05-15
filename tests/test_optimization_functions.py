import numpy as np
import os
import pandas as pd
import pickle

from copy import deepcopy

from rec_sizing.optimization_functions import (
	run_clustering_kmedoids,
	run_pre_collective_pool_milp
)
from rec_sizing.clustering.structures.I_O_clustering import (
	CLUSTERING_INPUTS,
	CLUSTERING_OUTPUTS
)
from rec_sizing.optimization.structures.I_O_collective_pool_milp import (
	INPUTS_CLUSTER_POOL,
	INPUTS_NO_INSTALL_POOL,
	OUTPUTS_CLUSTER_POOL,
	OUTPUTS_NO_INSTALL_POOL,
)


def test_run_clustering_kmedoids():
	# Assert the generation of the expected kmedoids
	# run clustering
	outputs = run_clustering_kmedoids(CLUSTERING_INPUTS)

	# compare outputs
	assert outputs == CLUSTERING_OUTPUTS


def test_run_pre_two_stage_collective_pool_milp():
	results = run_pre_collective_pool_milp(INPUTS_NO_INSTALL_POOL)
	round_cost = lambda x: {meter_id: round(cost, 3) for meter_id, cost in x.items()}
	results['obj_value'] = round(results['obj_value'], 3)
	results['c_ind2pool'] = round_cost(results['c_ind2pool'])
	results['dual_prices'] = [round(dp, 4) for dp in results['dual_prices']]
	for ki, valu in results.items():
		assert valu == OUTPUTS_NO_INSTALL_POOL.get(ki), f'{ki}'


def test_run_clustering_pre_two_stage_collective_pool_milp():
	inputs = deepcopy(INPUTS_CLUSTER_POOL)
	results = run_pre_collective_pool_milp(inputs)

	round_cost = lambda x: {meter_id: round(cost, 3) for meter_id, cost in x.items()}
	results['obj_value'] = round(results['obj_value'], 3)
	results['c_ind2pool'] = round_cost(results['c_ind2pool'])
	results['dual_prices'] = [round(dp, 4) for dp in results['dual_prices']]
	for ki, valu in results.items():
		assert valu == OUTPUTS_CLUSTER_POOL.get(ki), f'{ki}'


if __name__ == '__main__':
	test_run_clustering_kmedoids()
	test_run_pre_two_stage_collective_pool_milp()
	test_run_clustering_pre_two_stage_collective_pool_milp()
