"""post-processing calculates:
    - Desegregated O.F. costs: retailer exchanges; self-consumed tariff; contracted power; Batteries and PV investments
    - Total internal market compensation by installation
    - Total REC costs affected by the internal market compensation by installation
    - Total REC costs by member
    - Total REC costs affected by the internal market compensation by member
"""
import numpy as np

from rec_sizing.optimization.helpers.milp_helpers import (dict_none_lists, time_intervals)


def desegregated_OF_costs(results, inputs_opt):

    set_meters = list(inputs_opt['meters'])
    time_series = range(time_intervals(inputs_opt['nr_days'] * 24, inputs_opt['delta_t']))
    results = results.copy()
    results['retailer_exchanges_cost'] = {meter_id: None for meter_id in set_meters}
    results['sc_tariff_cost'] = {meter_id: None for meter_id in set_meters}
    results['contractedpower_cost'] = {meter_id: None for meter_id in set_meters}
    results['batteries_investments_cost'] = {meter_id: None for meter_id in set_meters}
    results['PV_investments_cost'] = {meter_id: None for meter_id in set_meters}
    # results['meter_cost'] = {meter_id: None for meter_id in set_meters}

    for n in set_meters:
        increment = f'{n}'
        # Exchanges costs with the main grid (buying and selling energy)
        results['retailer_exchanges_cost'][n] = (
            round(
                sum(
                    (
                            np.array(results['e_sup'][n]) * np.array(inputs_opt['meters'][n]['l_buy']) -
                            np.array(results['e_sur'][n]) * np.array(inputs_opt['meters'][n]['l_sell'])
                    ) *
                    results['w_clustering']
                ),
                5
            )
        )
        # Using Networks Costs for self-consumption (through assets)
        results['sc_tariff_cost'][n] = (
            round(
                sum(
                    np.array(results['e_slc_pool'][n] * np.array(inputs_opt['l_grid'])) * results['w_clustering']),
                5
            )
        )
        # Contracted Power Costs
        results['contractedpower_cost'][n] = (
            round(
                results['p_cont'][n] * inputs_opt['meters'][n]['l_cont'] * inputs_opt['nr_days_old'],
                5
            )
        )
        # Investment costs of individual and shared assets (CPE)
        results['batteries_investments_cost'][n] = (
            round(
                results['e_bn_new'][n] * inputs_opt['meters'][n]['l_bic'] * inputs_opt['nr_days_old'],
                5
            )
        )
        results['PV_investments_cost'][n] = (
            round(
                results['p_gn_new'][n] * inputs_opt['meters'][n]['l_gic'] * inputs_opt['nr_days_old'],
                5
            )
        )
        # results['meter_cost'][n] = (
        #     round(
        #         results['retailer_exchanges_cost'][n] +
        #         results['sc_tariff_cost'][n] +
        #         results['contractedpower_cost'][n] +
        #         results['batteries_investments_cost'][n] +
        #         results['PV_investments_cost'][n],
        #         4
        #     )
        # )

    return results


def post_processing_InternalMarket(results, inputs_opt):
    set_meters = list(inputs_opt['meters'])
    _time_intervals = time_intervals(inputs_opt['nr_days'] * 24, inputs_opt['delta_t'])
    time_series = range(_time_intervals)
    results = results.copy()
    # sold position energy (sold - bought) locally by n
    results['sold_position'] = dict_none_lists(_time_intervals, set_meters)
    for n in set_meters:
        e_pur = results['e_pur_pool'][n]
        e_sale = results['e_sale_pool'][n]
        results['sold_position'][n] = [e_sale - e_pur for e_sale, e_pur in zip(e_sale, e_pur)]

    # internal market compensations - Pool
    results['internal_market'] = {meter_id: None for meter_id in set_meters}
    for n in set_meters:
        results['internal_market'][n] = (
            round(
                sum(
                    (
                            np.array(results['dual_prices']) *
                            np.array(results['sold_position'][n])) *
                    results['w_clustering']
                ),
                4
            )
        )
    # validation of pool compensations
    if round(sum(results['internal_market'][n] for n in set_meters), 3) == 0:
        print('True: total costs internal market compensations = 0')
    else:
        print('False: total costs internal market compensations != 0')

    # installations costs with internal market compensations - Pool
    results['installation_cost_compensations'] = {meter_id: None for meter_id in set_meters}
    for n in set_meters:
        results['installation_cost_compensations'][n] = (
            round(
                results['c_ind2pool'][n] -
                results['internal_market'][n],
                4
            )
        )
    # validation installation cost with internal market compensations
    if (round(results['obj_value'], 2) ==
            round(sum(results['installation_cost_compensations'][n] for n in set_meters), 2)):
        print('True: total costs = sum of installations costs with compensations')
    else:
        print('False: total costs != sum of installations costs with compensations')

    return results


def post_processing_members(results, inputs_pp):
    set_meters = list(inputs_pp['ownership'])
    set_members = []
    for n in set_meters:
        set_members += list(inputs_pp['ownership'][n])
    set_members = list(set(set_members))
    results = results.copy()
    results['member_cost_installation'] = {key: {} for key in set_members}
    results['member_cost'] = {}
    results['member_cost_compensations_installation'] = {key: {} for key in set_members}
    results['member_cost_compensations'] = {}

    # costs by member
    for m in set_members:
        for n in set_meters:
            try:
                results['member_cost_installation'][m][n] = (
                    round(
                        results['c_ind2pool'][n] * inputs_pp['ownership'][n][m],
                        4
                    )
                )
                results['member_cost_compensations_installation'][m][n] = (
                    round(
                        results['installation_cost_compensations'][n] * inputs_pp['ownership'][n][m],
                        4
                    )
                )
            except:
                pass
    for m in set_members:
        results['member_cost'][m] = (
            round(
                sum(
                    results['member_cost_installation'][m][n]
                    for n in results['member_cost_installation'][m].keys()
                ),
                4
            )
        )
        results['member_cost_compensations'][m] = (
            round(
                sum(
                    results['member_cost_compensations_installation'][m][n]
                    for n in results['member_cost_compensations_installation'][m].keys()
                ),
                4
            )
        )

    # validation member cost
    if round(results['obj_value'], 2) == round(sum(results['member_cost'][m] for m in set_members), 2):
        print('True: total costs = sum of members costs')
    else:
        print('False: total costs != sum of members costs')
    # validation member cost with internal market compensations
    if (round(sum(results['installation_cost_compensations'][n] for n in set_meters), 2) ==
            round(sum(results['member_cost_compensations'][m] for m in set_members), 2)):
        print('True: sum installations costs with compensations = sum of members costs with compensations')
    else:
        print('False: sum installations costs with compensations != sum of members costs with compensations')

    return results
