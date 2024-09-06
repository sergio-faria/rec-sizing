from loguru import logger
from rec_sizing.optimization.module.post_processing import *

def run_post_processing(results_opt, inputs_opt, inputs_pp):
    """
    Use this functions to compute a post-processing results for a given optimized renewable energy community (REC)
    After run the sizing with the function "run_pre_collective_pool_milp()", this is able to compute the desegregated
    costs of the REC by installation: retailer exchanges; self-consumed tariff; contracted power; Batteries and PV
    investments.
    This functions also computes the internal market compensations (pool) that resulted by the optimization per
    installation.
    Finally, this function calculates the costs per member based on the installations ownership required as an input.
    The costs per member are also calculated with or without the internal market costs.
    :param results_opt: {
        this parameter refers to the results of the sizing optimization returned from "run_pre_collective_pool_milp()",
        as "results" variable. For more details on this variable's content check the function
        "run_pre_collective_pool_milp()" on "optimization_functions.py" file}
    :param inputs_opt: {
        this parameter refers to the inputs required to compute the sizing optimization also required on
        "run_pre_collective_pool_milp()" function, as "backpack". For more details on this variable's content check
        the function "run_pre_collective_pool_milp()" on "optimization_functions.py" file}
    :param inputs_pp: {
            'ownership': structure with the meters' ownership relative to each member
            {
                #meter_id: unique meter identifier requested in optimization process
                {
				    #member_id: unique REC member identifier that contains the meter/member pair ownership value [0;1]
                }
            }
        }
    :return: {the following results are added to a previous input parameter called "results_opt" on this function.
        That were previously returned from the function "run_pre_collective_pool_milp()" as "results" variable when
        the sizing optimization is computed. For more details on this variable's content check the function
        "run_pre_collective_pool_milp()" on "optimization_functions.py" file.
        'retailer_exchanges_cost': dict of floats with the retailer exchanges costs by installation for the optimization
            horizon, in €; positive values are costs, negative values are profits
        'sc_tariff_cost': dict of floats with the self-consumer tariff costs (grid access) by installation for the
            optimization horizon, in €;
        'contractedpower_cost': dict of floats with the contracted power costs by installation for the optimization
            horizon, in €;
        'batteries_investments_cost': dict of floats with the investments costs in batteries per installation
            for the optimization horizon, in €;
        'PV_investments_cost': dict of floats with the investments costs in PV per installation for the
            optimization horizon, in €;
        'sold_position': dict containing a list of floats with the energy trades (sells - purchases) in the internal
            market (REC) per installation for each timestamp, in kWh; positive values are sells and negative are purchases
        'internal_market': dict containing a list of floats with the energy trades costs in the internal market (REC)
            per installation for each timestamp, in €; positive values are costs and negative are profits
        'installation_cost_compensations': dict of floats with the installation costs compensated with the internal
            market per installation for the optimization horizon, in €;
        'member_cost_installation': dict of floats with the corresponding members costs per installation for the
            optimization horizon, in €;
        'member_cost': dict of floats with the members costs for the optimization horizon, in €;
        'member_cost_compensations_installation': dict of floats with the corresponding members costs per installation
            compensated with the internal market for the optimization horizon, in €;
        'member_cost_compensations': dict of floats with the members costs compensated with the internal market for the
            optimization horizon, in €;
    """
    logger.info('Compute the desegregated costs of the optimization (pool)')
    # the desegregated costs are added to the optimization results structure
    desegregated_costs = desegregated_OF_costs(results_opt, inputs_opt)

    logger.info('Compute the internal market compensations (pool)')
    # the internal market compensations per installations are added to the previous output structure (desegregated_costs)
    IM_compensations = post_processing_InternalMarket(desegregated_costs, inputs_opt)

    logger.info('Compute the REC costs per member (pool)')
    # the REC costs per member are added to the previous output structure (IM_compensations)
    members_costs = post_processing_members(IM_compensations, inputs_pp)

    logger.info('post-processing (pool)... DONE!')

    return members_costs

