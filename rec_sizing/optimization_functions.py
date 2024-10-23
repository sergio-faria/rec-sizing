import multiprocessing as mp
import numpy as np

from loguru import logger
from joblib import Parallel, delayed

from rec_sizing.clustering.module.Clustering import clustering_kmedoids
from rec_sizing.configs.configs import (
	MIPGAP,
	SOLVER,
	TIMEOUT
)
from rec_sizing.custom_types.clustering_types import (
	BackpackKMedoids,
	OutputsKMedoids
)
from rec_sizing.custom_types.collective_milp_pool_types import (
	BackpackCollectivePoolDict,
	OutputsCollectivePoolDict
)
from rec_sizing.optimization.helpers.general_helpers import iter_dt
from rec_sizing.optimization.module.CollectiveMILPPool import CollectiveMILPPool


def run_clustering_kmedoids(
		backpack: BackpackKMedoids) \
		-> OutputsKMedoids:
	"""
	Implements sklearn_extra's K-Medoids clustering algorithm to partition the given data for a given meter into
	user-defined number of clusters.
    Data must be provided in a fixed, yet configurable time step, in multiples of 1 day, and must include 4 series of
    data per day: generation PV factor, consumption in kWh and buying and selling opportunity costs in €/kWh.

	:param backpack: {
		'nr_days': int with the number of days considered in the raw data
		'delta_t': float or int with the optimization time step to be considered, in hours
		'nr_representative_days': int with the target number of clusters / medoids / representative days
		'timeseries_data': dict of dict with the data that will be subjected to the clustering process, per meter_id
		{
			'#meter_id': a key that uniquely identifies the meter for which the information is provided
			{
				'e_g_factor': array of float with the RES generation profile factor for the meter's location
				'e_c': array of float with the forecasted energy consumption behind the meter, in kWh
				'l_buy': array of float with the opportunity costs for buying energy from the retailer, in €/kWh
				'l_sell': array of float with the opportunity costs for selling energy to the retailer, in €/kWh
			}
		}
		'l_grid': array of float with the applicable tariffs of grid usage for self-consumption
	}

	:return: {
		'inertia': float indicating the inertia of the samples/cluster members/days, i.e., the sum of the samples
			distances to closest cluster centers (medoids). Can be interpreted as an intracluster distance measurement.
		'date_cluster_labels': array of dictionaries with the cluster label attributed to each date
			[
				{
					'date': date in format 'YYYY-mm-dd'
					'cluster': str with the cluster label attributed to that date
				}
			]
		'representative_e_g': array of dictionares with the RES generation profile factors
			of the medoids / representative days
		[
			{
				'cluster': str with the cluster label
				'values': array of floats with the RES generation profile factor for the meter's location
			}
		]
		'representative_e_c': array of dictionares with the load profiles of the medoids / representative days
		[
			{
				'cluster': str with the cluster label
				'values': array of floats with the forecasted energy consumption behind the meter, in kWh
			}
		]
		'representative_l_buy': array of dictionares with the buying opportunity costs
		of the medoid / representative day
		[
			{
				'cluster': str with the cluster label
				'values': array of floats with the opportunity costs for buying energy from the retailer, in €/kWh
			}
		]
		'representative_l_sell': array of dictionares with the selling opportunity costs
		of the medoid / representative day
		[
			{
				'cluster': str with the cluster label
				'values': array of floats with the opportunity costs for selling energy to the retailer, in €/kWh
			}
		]
		'cluster_nr_days': array with the number of days on each cluster
		[
			{
				'cluster': str with the cluster label
				'value': number of days in the cluster
			}
		]
	}
	"""
	logger.info('Clustering provided data using KMedoids...')

	outputs = clustering_kmedoids(backpack)

	logger.info('Clustering provided data using KMedoids... DONE!')

	return outputs


def run_pre_collective_pool_milp(
		backpack: BackpackCollectivePoolDict,
		solver=SOLVER,
		timeout=TIMEOUT,
		mipgap=MIPGAP) \
		-> OutputsCollectivePoolDict:
	"""
	Use this function to compute a standalone collective MILP for a given renewable energy community (REC) or citizens
	energy community (CEC) under a pool market structure.
	This function is specific for a pre-delivery timeframe, providing the schedules for controllable assets,
	such as battery energy storage systems (BESS, presently the only modelled controllable assets) for days- to
	years-ahead, optimal transactions between REC members and optimal investments in new storage and/or RES capacities.
	The function requires the provision of several forecasts, parameters and other data which thoroughly described
	below, under the parameter "backpack". Arrays with time-varying data such as consumption/generation forecasts and
	opportunity costs must comply with the expected length defined by the MILP's horizon and step
	(e.g., for a 24h horizon, and a step of 15 minutes or 0.25 hours, the length of the arrays must be 96).

	:param backpack: {
		'nr_days': an int with the number of days to consider in the optimization
		'nr_clusters': an int (optional) with the number of representative days that will be considered after applying a
			clustering method to time series data (e_c, e_g_factor, l_buy and l_sell);
			when setting this value, the MILP will run over the clustered data, with #nr_clusters days worth of data,
			reducing the computational burden but integrating some error in the results, as big as the difference
			between nr_days and nr_clusters;
			this value will default to nr_days if nr_clusters > nr_days is provided or if nr_clusters is not provided
		'l_grid': an array with the applicable tariffs for self-consumed energy, in €/kWh
		'delta_t': a float or int with the optimization time step to be considered, in hours
		'storage_ratio': a float or int indicating a reference ratio between maximum admissible input and output storage
			power and storage nominal capacity, in kW/kWh; this fundamental ratio will be considered for any storage
			asset installation suggestion by the MILP
		'strict_pos_coeffs': boolean indicating if the (dynamic) allocation coefficients that are generated by the
			internal REC transactions need to be strictly positive (as the Portuguese legislation currently demands)
			or not
		'total_share_coeffs': boolean indicating that meters with surplus must share all that surplus with meters that
			are consuming in the REC if the REC has a deficit (i.e., total consumption > total generation); on the
			other hand, if the REC has a surplus (i.e., total generation > total consumption), meters with surplus must
			share their surplus with consumming members up to their consumption, and the remaning surplus can be sold
			to the retailer; this implementation follows out interpretation of the curent Portuguese law.
		'meters': structure with information relative to each meter
		{
			#meter_id: {
				'l_buy': an array with the opportunity costs for buying energy from the retailer, in €/kWh
				'l_sell': an array with the opportunity costs for selling energy to the retailer, in €/kWh
				'l_cont': a float representing the contracted power tariff of the meter, adjusted to one day,
					in €/kW.day
				'l_gic': a float representing the investment cost for additional RES installation in the meter,
					adjusted to one day, in €/kW.day, i.e., €/kW / nr. of days in the considered panel's lifespan
				'l_bic': a float representing the investment cost for additional storage installation in the meter,
					adjusted to one day, in €/kW.day, i.e., €/kW / nr. of days in the considered battery's lifespan
				'e_c': an array with the forecasted energy consumption behind the meter, in kWh
				'p_meter_max': a float with the maximum capacity the meter can safely handle, in kW
				'p_gn_init': a float with te initial installed RES generation capacity at the meter, in kW
				'e_g_factor': an array with the RES generation profile factor for the meter's location
				'p_gn_min': a float representing the minimum RES capacity to be installed at the meter, in kW
				'p_gn_max': a float representing the maximum RES capacity to be installed at the meter, in kW
				'e_bn_init': a float with te initial installed storage capacity at the meter, in kW
				'e_bn_min': a float representing the minimum storage capacity to be installed at the meter, in kWh
				'e_bn_max': a float representing the maximum storage capacity to be installed at the meter, in kWh
				'soc_min': a percentage, applicable to "e_bn", identifying a minimum limit to the energy content
				'eff_bc': a fixed value, between 0 and 1, that expresses the charging efficiency of the BESS
				'eff_bd': a fixed value, between 0 and 1, that expresses the discharging efficiency of the BESS
				'soc_max': a percentage, applicable to "e_bn", identifying a maximum limit to the energy content
				'deg_cost': a float representing a penalty for cyclic degradation of the BESS, in €/kWh
				'btm_evs': structure where several Btm EVs units can be defined
					#EV_id: {
						'trip_ev': EV energy consumption, in kWh
						'min_energy_storage_ev': Minimum stored energy to be guaranteed for vehicle ev at CPE n, in kWh
						'battery_capacity_ev': The battery energy capacity of vehicle ev at CPE n, in kWh
						'eff_bc_ev': Charging efficiency of vehicle ev at CPE n, between 0 and 1
						'eff_bd_ev': Discharging efficiency of vehicle ev at CPE n, between 0 and 1
						'init_e_ev': the initial energy content of the EV, in kWh
						'pmax_c_ev': Maximum power charge of vehicle ev at CPE n, in kW
						'pmax_d_ev': Maximum power discharge of vehicle ev at CPE n, in kW
						'bin_ev': Whether a vehicle ev at CPE n is plugged-in or not (if plugged-in = 1 else = 0)
							}
				'ewh': structure where several EWH units can be defined
						'params_input': structure for EWH static parameters
							'load_diagram_exists': boolean variable that states if the provided dataset is the actual
													diagram (1), or the estimated hot water usage calendar (0)
							'ewh_specs': structure for EWH specifications
								'ewh_capacity': EWH capacity (l)
								'ewh_power': EWH heating power (W)
								'ewh_max_temp': EWH maximum allowed water temperature (°C)
								'ewh_std_temp': EWH standard non-optimized functioning water temperature (°C)
								'user_comf_temp': Hot-Water Usage Comfort Temperature (minimum user-defined temperature - °C)
								'tariff': Tariff selection between simple (1) or dual (2)
								'price_simple': Simple pricing value per kWh (Euro)
								'price_dual_day': Dual day pricing value per kWh (Euro)
								'price_dual_night': Dual night pricing value per kWh (Euro)
								'tariff_simple':  Fixed daily simple tariff pricing (Euro)
								'tariff_dual': Fixed daily dual tariff pricing (Euro)
						'dataset': contains the actual EWH dataset. The user can provide the real load time-series, or
									the estimated hot-water usage calendar. The load time-series should respect a 1-min
									measurement resolution, with 'timestamp' and 'load' pairwise keys. The estimated
									usage should have the usages starting timestamp in the 'start' key, and the duration
									in the 'duration' key.
			}
		}
	}

	:param solver: a string with the solver chosen for the MILP. For the meantime, the library accepts the values "CBC"
	"CPLEX" and "HiGHS", with any other string passed being defaulted to "CBC", with a warning.
	Note that, since CPLEX is a commercial solver, and HiGHS does not come with puLP, you need to install
	them first to be able to use them.
	 - HiGHS: just run "conda install -c conda-forge highs" in your active conda environment

	:param timeout: an integer representing a temporal limit for the solver to find an optimal solution (s)

	:param mipgap: a float for controlling the solver's tolerance; intolerant [0 - 1] fully permissive; any value
	outside this range will be reverted to the default 0.01, with a warning.

	:return: {
		'obj_value': float with value obtained for the objective function under an optimal solution of the MILP
		'milp_status': string with the status of the optimization problem; only non-error value is "Optimal"
		'p_cont': dict of floats with the minimum contracted power required per meter, in kW
		'p_gn_new': dict of floats with the suggested increase in PV capacity per meter, in kW
		'p_gn_total': dict of floats with the initial + suggested increase in PV capacity per meter, in kW
		'e_bn_new': dict of floats with the suggested increase in storage capacity per meter, in kWh
		'e_bn_total': dict of floats with the initial + suggested increase in storage capacity per meter, in kWh
		'e_cmet': dict of float arrays with the net load consumptions forecasted per time step and per meter, in kWh
		'e_g': dict of float arrays with the forecasted total PV generation per time step and per meter, in kWh
		'e_bc': dict of float arrays with the charging energy setpoints for each storage asset, in kWh
		'e_bd': dict of float arrays with the discharging energy setpoints for each storage asset, in kWh
		'e_sup_retail': dict of float arrays with energy bought from the retailer per time step and per meter, in kWh
		'e_sur_retail': dict of float arrays with energy sold to the retailer per time step and per meter, in kWh
		'e_pur_pool': dict of float arrays with the energy bought on the LEM per time step and per meter, in kWh
		'e_sale_pool': dict of float arrays with the energy sold on the LEM per time step and per meter, in kWh
		'e_slc_pool': dict of float arrays with the self-consumed energy per time step and per meter, in kWh
		'e_bat': dict of float arrays with the total storage energy content per time step and per meter, in kWh
		'delta_sup': dict of float arrays with auxiliary binary values per time step and per meter
		'e_consumed': dict of float arrays with auxiliary continuous values per time step and per meter
		'e_alc': dict of float arrays with auxiliary continuous values per time step and per meter
		'delta_slc': dict of float arrays with auxiliary binary values per time step and per meter
		'delta_cmet': dict of float arrays with auxiliary binary values per time step and per meter
		'delta_alc': dict of float arrays with auxiliary binary values per time step and per meter
		'delta_coeff': dict of float arrays with auxiliary binary values per time step and per meter
		'delta_rec_balance': float array with auxiliary binary values per time step and per meter
		'delta_meter_balance': dict of float arrays with auxiliary binary values per time step and per meter
		'c_ind2pool': dict of floats with the individual costs with energy for the optimization horizon, in €;
			positive values are costs, negative values are profits
		'dual_prices: float array with the market equilibrium shadow prices to be used as LEM prices, in €/kWh
		'ewh_temp' dict of floats fot EWH internal water temperature, per time step, per meter
		'ewh_delta_in': dict of floats for EWH Functioning (ON/OFF) Calendar (relative to the used resolution),
			per time step, per meter
		'ewh_delta_use' dict of bool with EWH hot water usage, per time step, per meter
		'ewh_optimized_load': dict of floats for EWH optimized load diagram, per time step, per meter
		'ewh_original_load': dict of floats for EWH original load diagram, per time step, per meter
	}
	"""
	logger.info('Running a pre-delivery standalone/second stage collective (pool) MILP...')

	# -- DEFAULTS AND WARNINGS -----------------------------------------------------------------------------------------
	# Default solver in case of non-valid option
	if solver not in ['CBC', 'CPLEX', 'HiGHS']:
		logger.warning(f'solver = {solver} not recognized; reverting to {SOLVER}')
		solver = SOLVER

	# Default timeout in case of non-valid option
	if timeout < 0:
		logger.warning(f'timeout < 0; reverting to default {TIMEOUT}')
		timeout = TIMEOUT

	# Default mipgap in case of non-valid option
	if mipgap < 0:
		logger.warning(f'mipgap < 0; reverting to default {MIPGAP}')
		mipgap = MIPGAP
	elif mipgap > 1:
		logger.warning(f'mipgap > 1; reverting to default {MIPGAP}')
		mipgap = MIPGAP

	# Default the number of clusters in case of non-valid option;
	# define nr_clusters = nr_days in case nr_clusters was not provided (i.e., do not clusterize data)
	nr_clusters = backpack.get('nr_clusters')
	nr_days = backpack.get('nr_days')
	nr_dates = nr_days
	if nr_clusters is not None:
		if nr_clusters > nr_days:
			logger.warning(f'nr_clusters > nr_days')
			nr_clusters = nr_days
			backpack['nr_clusters'] = nr_days
	else:
		nr_clusters = nr_days
		backpack['nr_days_old'] = nr_days
		backpack['nr_clusters'] = nr_days

	# Default the grid tariffs' array in case of non-valid option
	if backpack.get('l_grid') is not None:
		if (np.array(backpack.get('l_grid')) < 0).any():
			logger.warning(f'One or more l_grid < 0; those tariffs will be set to 0.0')
			backpack['l_grid'] = [abs(tar) for tar in backpack['l_grid']]

	# -- CLUSTERING ----------------------------------------------------------------------------------------------------
	# Apply clustering to timeseries data (one meter at a time)
	delta_t = backpack.get('delta_t')
	nr_data_points = int(nr_days * 24 / delta_t)

	if nr_days != nr_clusters:
		# Create inputs for clustering method
		meters = backpack.get('meters')
		inputs_clustering = {
			'nr_days': nr_days,
			'delta_t': delta_t,
			'nr_representative_days': nr_clusters,
			'l_grid': backpack['l_grid'],
			'timeseries_data': {
				meter_id: {
					'e_g_factor': backpack['meters'][meter_id]['e_g_factor'],
					'e_c': backpack['meters'][meter_id]['e_c'],
					'l_buy': backpack['meters'][meter_id]['l_buy'],
					'l_sell': backpack['meters'][meter_id]['l_sell']
				}
				for meter_id in meters
			}
		}

		# Run clustering
		clustered_inputs = run_clustering_kmedoids(inputs_clustering)

		# Substitute the daily data by the representative data
		for meter_id, meter_data in meters.items():
			backpack['meters'][meter_id]['e_g_factor'] = []
			backpack['meters'][meter_id]['e_c'] = []
			backpack['meters'][meter_id]['l_buy'] = []
			backpack['meters'][meter_id]['l_sell'] = []

			for cl in range(nr_clusters):
				backpack['meters'][meter_id]['e_g_factor'] += \
					clustered_inputs['representative_e_g_factor'][meter_id][str(cl)]
				backpack['meters'][meter_id]['e_c'] += \
					clustered_inputs['representative_e_c'][meter_id][str(cl)]
				backpack['meters'][meter_id]['l_buy'] += \
					clustered_inputs['representative_l_buy'][meter_id][str(cl)]
				backpack['meters'][meter_id]['l_sell'] += \
					clustered_inputs['representative_l_sell'][meter_id][str(cl)]

		backpack['l_grid'] = []
		backpack['w_clustering'] = []
		nr_daily_data_points = int(24 / delta_t)

		for cl in range(nr_clusters):
			backpack['l_grid'] += clustered_inputs['representative_l_grid'][str(cl)]
			backpack['w_clustering'] += [clustered_inputs['cluster_nr_days'][str(cl)]] * nr_daily_data_points
		backpack['nr_days_old'] = nr_days
		backpack['nr_days'] = nr_clusters

	# Use timeseries data as is, effectively running the MILP with nr_days as the total number of days worth of data
	else:
		backpack['w_clustering'] = [1] * nr_data_points

	# -- RUN MILP ------------------------------------------------------------------------------------------------------
	logger.info(' - defining MILP -')
	milp = CollectiveMILPPool(backpack, nr_dates, solver, timeout, mipgap)

	nr_days = backpack.get('nr_days')
	logger.info(f' - MILP set with an horizon of {nr_days} days, mipgap={mipgap}, timeout={timeout}, solver={solver} -')

	logger.info(' - solving MILP -')
	milp.solve_milp()

	logger.info(' - generating outputs -')
	results = milp.generate_outputs()

	logger.info('Running a pre-delivery standalone/second stage collective (pool) MILP... DONE!')

	return results
