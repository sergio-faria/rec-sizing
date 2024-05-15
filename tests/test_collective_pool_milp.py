from copy import deepcopy

from rec_sizing.optimization.module.CollectiveMILPPool import CollectiveMILPPool
from rec_sizing.optimization.structures.I_O_collective_pool_milp import (
	INPUTS_INSTALL_POOL,
	INPUTS_NO_INSTALL_POOL,
	OUTPUTS_INSTALL_POOL,
	OUTPUTS_NO_INSTALL_POOL
)


def test_solve_collective_pool_milp_no_install():
	inputs = deepcopy(INPUTS_NO_INSTALL_POOL)
	inputs['w_clustering'] = [1] * 3

	# Assert the creation of a correct class
	milp = CollectiveMILPPool(inputs)
	assert isinstance(milp, CollectiveMILPPool)

	# Assert the MILP is optimally solved
	milp.solve_milp()
	assert milp.status == 'Optimal'

	# Assert the correct ouputs
	results = milp.generate_outputs()
	round_cost = lambda x: {meter_id: round(cost, 3) for meter_id, cost in x.items()}
	results['obj_value'] = round(results['obj_value'], 3)
	results['c_ind2pool'] = round_cost(results['c_ind2pool'])
	results['dual_prices'] = [round(dp, 4) for dp in results['dual_prices']]
	for ki, valu in results.items():
		assert valu == OUTPUTS_NO_INSTALL_POOL.get(ki), f'{ki}'


def test_solve_collective_pool_milp_yes_install():
	inputs = deepcopy(INPUTS_INSTALL_POOL)
	inputs['w_clustering'] = [1] * 3

	# Assert the creation of a correct class
	milp = CollectiveMILPPool(inputs)
	assert isinstance(milp, CollectiveMILPPool)

	# Assert the MILP is optimally solved
	milp.solve_milp()
	assert milp.status == 'Optimal'

	# Assert the correct ouputs
	results = milp.generate_outputs()
	round_cost = lambda x: {meter_id: round(cost, 3) for meter_id, cost in x.items()}
	results['obj_value'] = round(results['obj_value'], 3)
	results['c_ind2pool'] = round_cost(results['c_ind2pool'])
	results['dual_prices'] = [round(dp, 4) for dp in results['dual_prices']]
	for ki, valu in results.items():
		assert valu == OUTPUTS_INSTALL_POOL.get(ki), f'{ki}'


if __name__ == '__main__':
	test_solve_collective_pool_milp_no_install()
	test_solve_collective_pool_milp_yes_install()
