from rec_sizing.optimization_functions import (
	run_pre_collective_pool_milp
)
from rec_sizing.optimization.structures.I_O_collective_pool_milp import (
	INPUTS_NO_INSTALL_POOL,
	OUTPUTS_NO_INSTALL_POOL
)


def test_run_pre_two_stage_collective_pool_milp():
	results = run_pre_collective_pool_milp(INPUTS_NO_INSTALL_POOL)
	round_cost = lambda x: {meter_id: round(cost, 3) for meter_id, cost in x.items()}
	results['obj_value'] = round(results['obj_value'], 3)
	results['c_ind2pool'] = round_cost(results['c_ind2pool'])
	results['dual_prices'] = [round(dp, 4) for dp in results['dual_prices']]
	for ki, valu in results.items():
		assert valu == OUTPUTS_NO_INSTALL_POOL.get(ki), f'{ki}'
