"""
Class for implementing and running the Stage 2 MILP for an energy community.
The implementation is specific to a pool market structure.
"""
import itertools
import numpy as np
import os
import re

from rec_sizing.configs.configs import (
	MIPGAP,
	SOLVER,
	TIMEOUT
)
from rec_sizing.optimization.helpers.milp_helpers import (
	dict_none_lists,
	dict_per_param,
	none_lists,
	round_up,
	time_intervals
)
from rec_sizing.custom_types.collective_milp_pool_types import (
	BackpackCollectivePoolDict,
	OutputsCollectivePoolDict
)
from loguru import logger
from pulp import (
	CPLEX_CMD,
	listSolvers,
	LpBinary,
	LpMinimize,
	LpProblem,
	LpStatus,
	lpSum,
	LpVariable,
	pulp,
	value
)


class CollectiveMILPPool:
	def __init__(self, backpack: BackpackCollectivePoolDict, solver=SOLVER, timeout=TIMEOUT, mipgap=MIPGAP):
		# Indices and sets
		self._nr_days = backpack.get('nr_days')  # operation period (days)
		self._horizon = None  # operation period (hours)
		# Parameters
		self._l_buy = None  # supply energy tariff [€/kWh]
		self._l_sell = None  # feed in energy tariff [€/kWh]
		self._l_grid = backpack.get('l_grid')  # access tariff of the local grid [€/kWh]
		self._l_cont = None  # contracted power tariff, adjusted to one day [€/kW.day]
		self._days = None  # number of days in the optimization horizon [days]
		self._l_gic = None  # investment cost for RES installation, adjusted to one day [€/kW.day]
		self._l_bic = None  # investment cost for storage installation, adjusted to one day [€/kWh.day]
		self._e_c = None  # meter load profile [kWh]
		self._p_meter_max = None  # meters' power limit (constrains total contracted power) [kWh]
		self._p_gn_init = None  # initial installed RES capacity [kW]
		self._e_g_factor = None  # generation profile factor of RES for the meter's location (multiplies by kWh)
		self._delta_t = backpack.get('delta_t')  # interval settlement duration [h]
		self._p_gn_min = None  # minimum RES capacity to be installed
		self._p_gn_max = None  # maximum RES capacity to be installed
		self._e_bn_init = None  # initial installed storage capacity [kW]
		self._e_bn_min = None  # minimum storage capacity to be installed
		self._e_bn_max = None  # maximum storage capacity to be installed
		self._storage_ratio = backpack.get('storage_ratio')  # ratio between the reference maximum admissible input and
		# output storage power and the reference storage nominal capacity.
		self._soc_min = None  # minimum state of charge of the storage systems in the meter [%]
		self._eff_bc = None  # charging efficiency of the storage systems in the meter [%]
		self._eff_bd = None  # discharging efficiency of the storage systems in the meter [%]
		self._soc_max = None  # maximum state of charge of the storage systems in the meter [%]
		self._big_m = None  # a very big number [kWh]
		# MILP variables
		self.solver = solver  # solver chosen for the MILP
		self.timeout = timeout  # solvers temporal limit to find optimal solution (s)
		self.mipgap = mipgap  # controls the solver's tolerance; intolerant [0 - 1] fully permissive
		self.regulatory_context = "General"  # can be one of "General" or "Portuguese" - for constraint (3)
		self.strict_pos_coeffs = backpack.get('strict_pos_coeffs')  # no negative coefficients if True
		self.total_share_coeffs = backpack.get('total_share_coeffs')  # share all required in the REC if True
		self._meters_data = backpack.get('meters')  # data from Meters
		self.milp = None  # for storing the MILP formulation
		self.status = None  # stores the status of the MILP's solution
		self.obj_value = None  # stores the MILP's numeric solution
		self.time_intervals = None  # for number of time intervals per horizon
		self.time_series = None  # for a range of time intervals
		self.set_meters = None  # set with Meters' ID

	def __define_milp(self):
		"""
		Method to define the collective MILP problem.
		"""
		logger.debug(f'-- defining the collective (pool) MILP problem...')

		# Define a minimization MILP
		self.milp = LpProblem(f'collective_pool', LpMinimize)

		# Additional temporal variables
		self._horizon = self._nr_days * 24
		self.time_intervals = time_intervals(self._horizon, self._delta_t)
		self.time_series = range(self.time_intervals)

		# Set of Meters
		self.set_meters = list(self._meters_data.keys())

		# For simplicity, unpack Meters' information into lists, by type of data, where each Meter is solely
		# identified by its relative position on the list
		self._l_buy = dict_per_param(self._meters_data, 'l_buy')
		self._l_sell = dict_per_param(self._meters_data, 'l_sell')
		self._l_cont = dict_per_param(self._meters_data, 'l_cont')
		self._l_gic = dict_per_param(self._meters_data, 'l_gic')
		self._l_bic = dict_per_param(self._meters_data, 'l_bic')
		self._e_c = dict_per_param(self._meters_data, 'e_c')
		self._p_meter_max = dict_per_param(self._meters_data, 'p_meter_max')
		self._big_m = 2 * max(self._p_meter_max.values())
		self._p_gn_init = dict_per_param(self._meters_data, 'p_gn_init')
		self._e_g_factor = dict_per_param(self._meters_data, 'e_g_factor')
		self._p_gn_min = dict_per_param(self._meters_data, 'p_gn_min')
		self._p_gn_max = dict_per_param(self._meters_data, 'p_gn_max')
		self._e_bn_init = dict_per_param(self._meters_data, 'e_bn_init')
		self._e_bn_min = dict_per_param(self._meters_data, 'e_bn_min')
		self._e_bn_max = dict_per_param(self._meters_data, 'e_bn_max')
		self._soc_min = dict_per_param(self._meters_data, 'soc_min')
		self._eff_bc = dict_per_param(self._meters_data, 'eff_bc')
		self._eff_bd = dict_per_param(self._meters_data, 'eff_bd')
		self._soc_max = dict_per_param(self._meters_data, 'soc_max')

		# Initialize the decision variables
		# contracted power tariff by n [kW]
		p_cont = {meter_id: None for meter_id in self.set_meters}
		# new installed RES capacity at n [kW]
		p_gn_new = {meter_id: None for meter_id in self.set_meters}
		# total installed RES capacity at n [kW]
		p_gn_total = {meter_id: None for meter_id in self.set_meters}
		# new installed storage system(s)  capacity at n [kW]
		e_bn_new = {meter_id: None for meter_id in self.set_meters}
		# total installed storage system(s) capacity at n [kW]
		e_bn_total = {meter_id: None for meter_id in self.set_meters}
		# net consumption at meter n [kWh]
		e_cmet = dict_none_lists(self.time_intervals, self.set_meters)
		# behind-the-meter generation at meter n [kWh]
		e_g = dict_none_lists(self.time_intervals, self.set_meters)
		# energy charged by meter n's storage system(s) [kWh]
		e_bc = dict_none_lists(self.time_intervals, self.set_meters)
		# energy charged by meter n's storage system(s) [kWh]
		e_bd = dict_none_lists(self.time_intervals, self.set_meters)
		# energy supplied to n from its retailer [kWh]
		e_sup = dict_none_lists(self.time_intervals, self.set_meters)
		# energy surplus sold by n to its retailer [kWh]
		e_sur = dict_none_lists(self.time_intervals, self.set_meters)
		# energy bought locally by n
		e_pur = dict_none_lists(self.time_intervals, self.set_meters)
		# energy sold locally by n
		e_sale = dict_none_lists(self.time_intervals, self.set_meters)
		# energy self-consumed by n (in theory, g.t.e. that value)
		e_slc = dict_none_lists(self.time_intervals, self.set_meters)
		# when True allows charge, else discharge
		delta_bc = dict_none_lists(self.time_intervals, self.set_meters)
		# energy stored by the storage system(s) in n [kWh]
		e_bat = dict_none_lists(self.time_intervals, self.set_meters)
		# when True allows supply when false allows surplus
		delta_sup = dict_none_lists(self.time_intervals, self.set_meters)
		# consumption at meter n (in theory, g.t.e. that value)
		e_consumed = dict_none_lists(self.time_intervals, self.set_meters)
		# consumed energy bought locally by n (in theory, g.t.e. that value)
		e_alc = dict_none_lists(self.time_intervals, self.set_meters)
		# auxiliary binary variable for defining self-consumed energy by n
		delta_slc = dict_none_lists(self.time_intervals, self.set_meters)
		# for defining e_consumed when a particular self._l_grid[t] is negative
		delta_cmet = dict_none_lists(self.time_intervals, self.set_meters)
		# for defining e_alc when a particular self._l_grid[t] is negative
		delta_alc = dict_none_lists(self.time_intervals, self.set_meters)
		if self.strict_pos_coeffs:
			# auxiliary binary variable for imposing positive allocation coefficients
			delta_coeff = dict_none_lists(self.time_intervals, self.set_meters)
		if self.total_share_coeffs:
			# auxiliary binary variable for signaling if the REC has a surplus or a deficit
			delta_rec_balance = none_lists(self.time_intervals)
			# auxiliary binary variable for signaling if a meter has a surplus or a deficit
			delta_meter_balance = dict_none_lists(self.time_intervals, self.set_meters)

		# Define the decision variables as puLP objets
		if self.total_share_coeffs:
			for t in self.time_series:
				increment = f't{t:03d}'
				delta_rec_balance[t] = LpVariable('delta_rec_balance_' + increment, cat=LpBinary)

		for n in self.set_meters:
			increment = f'{n}'
			p_cont[n] = LpVariable('p_cont_' + increment, lowBound=0)
			p_gn_new[n] = LpVariable('p_gn_new_' + increment, lowBound=0)
			p_gn_total[n] = LpVariable('p_gn_total_' + increment, lowBound=0)
			e_bn_new[n] = LpVariable('e_bn_new_' + increment, lowBound=0)
			e_bn_total[n] = LpVariable('e_bn_total_' + increment, lowBound=0)

		t_n_series = itertools.product(self.set_meters, self.time_series)  # iterates over each Meter and each time step
		for n, t in t_n_series:
			increment = f'{n}_t{t:03d}'
			e_cmet[n][t] = LpVariable('e_cmet_' + increment)
			e_g[n][t] = LpVariable('e_g_' + increment, lowBound=0)
			e_bc[n][t] = LpVariable('e_bc_' + increment, lowBound=0)
			e_bd[n][t] = LpVariable('e_bd_' + increment, lowBound=0)
			e_sup[n][t] = LpVariable('e_sup_' + increment, lowBound=0)
			e_sur[n][t] = LpVariable('e_sur_' + increment, lowBound=0)
			e_pur[n][t] = LpVariable('e_pur_' + increment, lowBound=0)
			e_sale[n][t] = LpVariable('e_sale_' + increment, lowBound=0)
			e_slc[n][t] = LpVariable('e_slc_' + increment, lowBound=0)
			delta_bc[n][t] = LpVariable('delta_bc_' + increment, cat=LpBinary)
			e_bat[n][t] = LpVariable('e_bat_' + increment, lowBound=0)
			delta_sup[n][t] = LpVariable('delta_sup_' + increment, cat=LpBinary)
			e_consumed[n][t] = LpVariable('e_consumed_' + increment, lowBound=0)
			e_alc[n][t] = LpVariable('e_alc_' + increment, lowBound=0)
			delta_slc[n][t] = LpVariable('delta_slc_' + increment, cat=LpBinary)
			delta_cmet[n][t] = LpVariable('delta_cmet_' + increment, cat=LpBinary)
			delta_alc[n][t] = LpVariable('delta_alc_' + increment, cat=LpBinary)
			if self.strict_pos_coeffs:
				delta_coeff[n][t] = LpVariable('delta_coeff_' + increment, cat=LpBinary)
			if self.total_share_coeffs:
				delta_meter_balance[n][t] = LpVariable('delta_meter_balance_' + increment, cat=LpBinary)

		# Eq. 1: Objective Function
		objective = lpSum(
			lpSum(
				e_sup[n][t] * self._l_buy[n][t]
				- e_sur[n][t] * self._l_sell[n][t]
				+ e_slc[n][t] * self._l_grid[t]
				for t in self.time_series
			)
			+ p_cont[n] * self._l_cont[n] * self._nr_days
			+ p_gn_new[n] * self._l_gic[n] * self._nr_days
			+ e_bn_new[n] * self._l_bic[n] * self._nr_days
			for n in self.set_meters
		)

		self.milp += objective, 'Objective Function'

		# Eq. 2-35: Constraints
		for t in self.time_series:
			increment = f'{t:03d}'

			# Eq. 19
			self.milp += \
				lpSum(e_pur[n][t] for n in self.set_meters) == lpSum(e_sale[n][t] for n in self.set_meters), \
				'Market_equilibrium_' + increment

			if self.total_share_coeffs:
				# Eq. 33
				self.milp += \
					lpSum(e_cmet[n][t] for n in self.set_meters) >= - self._big_m * delta_rec_balance[t], \
					'Check_REC_surplus_' + increment

				# Eq. 34
				self.milp += \
					lpSum(e_cmet[n][t] for n in self.set_meters) <= self._big_m * (1 - delta_rec_balance[t]), \
					'Check_REC_deficit_' + increment

		for n in self.set_meters:
			increment = f'{n}'

			# Eq. 5
			self.milp += \
				p_cont[n] <= self._p_meter_max[n], \
				'Contracted_power_limit' + increment

			# Eq. 6
			self.milp += \
				p_gn_new[n] == p_gn_total[n] - self._p_gn_init[n], \
				'New_gen_installed_' + increment

			# Eq. 8
			self.milp += \
				self._p_gn_min[n] <= p_gn_new[n], \
				'Min_new_gen_' + increment

			self.milp += \
				p_gn_new[n] <= self._p_gn_max[n], \
				'Max_new_gen_' + increment

			# Eq. 9
			self.milp += \
				e_bn_new[n] == e_bn_total[n] - self._e_bn_init[n], \
				'New_storage_installed_' + increment

			# Eq. 10
			self.milp += \
				self._e_bn_min[n] <= e_bn_new[n], \
				'Min_new_storage_' + increment

			self.milp += \
				e_bn_new[n] <= self._e_bn_max[n], \
				'Max_new_storage_' + increment

		for n, t in itertools.product(self.set_meters, self.time_series):
			increment = f'{n}_t{t:03d}'

			# Eq. 2
			self.milp += \
				e_cmet[n][t] == self._e_c[n][t] - e_g[n][t] + e_bc[n][t] - e_bd[n][t], \
				'C_met_' + increment

			# Eq. 3
			match self.regulatory_context:
				# Specific for the portuguese legislation
				case "Portuguese":
					self.milp += \
						e_cmet[n][t] == e_sup[n][t] - e_sur[n][t] + e_slc[n][t] - e_sale[n][t], \
						'Equilibrium_' + increment
				# General case (original formulation)
				case _:
					self.milp += \
						e_cmet[n][t] == e_sup[n][t] - e_sur[n][t] + e_pur[n][t] - e_sale[n][t], \
						'Equilibrium_' + increment

			# Eq. 4
			self.milp += \
				- p_cont[n] <= e_cmet[n][t] * 1 / self._delta_t, \
				'P_flow_low_limit_' + increment

			self.milp += \
				e_cmet[n][t] * 1 / self._delta_t <= p_cont[n], \
				'P_flow_high_limit_' + increment

			# Eq. 7
			self.milp += \
				e_g[n][t] == self._e_g_factor[n][t] * p_gn_total[n] * self._delta_t, \
				'Scaled_generation_' + increment

			# Eq. 11
			self.milp += \
				e_bc[n][t] * 1 / self._delta_t <= e_bn_total[n] * self._storage_ratio, \
				'Charge_rate_limit_' + increment

			# Eq. 12
			self.milp += \
				e_bd[n][t] * 1 / self._delta_t <= e_bn_total[n] * self._storage_ratio, \
				'Discharge_rate_limit' + increment

			# Eq. 13
			self.milp += \
				e_bc[n][t] * 1 / self._delta_t <= self._big_m * delta_bc[n][t], \
				'No_simultaneous_charge_discharge_C_' + increment

			# Eq. 14
			self.milp += \
				e_bd[n][t] * 1 / self._delta_t <= self._big_m * (1 - delta_bc[n][t]), \
				'No_simultaneous_charge_discharge_D_' + increment

			energy_update = e_bc[n][t] * self._eff_bc[n] - e_bd[n][t] * 1 / self._eff_bd[n]
			if t == 0:
				# Eq. 15
				init_e_bat = self._soc_min[n] / 100 * e_bn_total[n]

				# Eq. 16
				self.milp += \
					e_bat[n][t] == init_e_bat + energy_update, \
					'Energy_update_' + increment
			else:

				# Eq. 17
				self.milp += \
					e_bat[n][t] == e_bat[n][t - 1] + energy_update, \
					'Energy_update_' + increment

			# Eq. 18
			self.milp += \
				e_bat[n][t] >= self._soc_min[n] / 100 * e_bn_total[n], \
				'Minimum_SOC_' + increment

			self.milp += \
				e_bat[n][t] <= self._soc_max[n] / 100 * e_bn_total[n], \
				'Maximum_SOC_' + increment

			# Eq. 20
			self.milp += \
				e_sup[n][t] <= self._big_m * delta_sup[n][t], \
				'Supply_ON_' + increment

			self.milp += \
				e_sur[n][t] <= self._big_m * (1 - delta_sup[n][t]), \
				'Supply_OFF_' + increment

			if self._l_grid[t] >= 0:
				# Eq. 21
				self.milp += \
					e_consumed[n][t] >= e_cmet[n][t], \
					'Consumption_' + increment

				# Eq. 22
				self.milp += \
					e_alc[n][t] >= e_pur[n][t] - e_sale[n][t], \
					'Allocated_energy_' + increment

				# Eq. 23
				self.milp += \
					e_slc[n][t] >= e_consumed[n][t] - self._big_m * (1 - delta_slc[n][t]), \
					'Self_consumption_1_' + increment

				# Eq. 24
				self.milp += \
					e_slc[n][t] >= e_alc[n][t] - self._big_m * delta_slc[n][t], \
					'Self_consumption_2_' + increment

				# Eq. aux
				self.milp += \
					delta_cmet[n][t] == 0, \
					'Consumption_bin_' + increment

				# Eq. aux
				self.milp += \
					delta_alc[n][t] == 0, \
					'Allocated_energy_bin_' + increment

			else:
				# Eq. 25
				self.milp += \
					e_consumed[n][t] <= e_cmet[n][t] + self._big_m * delta_cmet[n][t], \
					'Consumption_1_' + increment

				# Eq. 26
				self.milp += \
					e_consumed[n][t] <= self._big_m * (1 - delta_cmet[n][t]), \
					'Consumption_2_' + increment

				# Eq. 27
				self.milp += \
					e_alc[n][t] <= e_pur[n][t] - e_sale[n][t] + self._big_m * delta_alc[n][t], \
					'Allocated_energy_1_' + increment

				# Eq. 28
				self.milp += \
					e_alc[n][t] <= self._big_m * (1 - delta_alc[n][t]), \
					'Allocated_energy_2_' + increment

				# Eq. 29
				self.milp += \
					e_slc[n][t] <= e_consumed[n][t], \
					'Self_consumption_1_' + increment

				# Eq. 30
				self.milp += \
					e_slc[n][t] <= e_alc[n][t], \
					'Self_consumption_2_' + increment

				# Eq. aux
				self.milp += \
					delta_slc[n][t] == 0, \
					'Self_consumed_energy_bin_' + increment

			if self.strict_pos_coeffs:
				# Eq. 31
				self.milp += \
					e_sale[n][t] - e_pur[n][t] <= -e_cmet[n][t] + self._big_m * delta_coeff[n][t], \
					'Positive_coefficients_1_' + increment

				# Eq. 32
				self.milp += \
					e_sale[n][t] - e_pur[n][t] <= self._big_m * (1 - delta_coeff[n][t]), \
					'Positive_coefficients_2_' + increment

			if self.total_share_coeffs:
				# Eq. 35
				self.milp += \
					e_cmet[n][t] >= - self._big_m * delta_meter_balance[n][t], \
					'Check_meter_surplus_' + increment

				# Eq. 36
				self.milp += \
					e_cmet[n][t] <= self._big_m * (1 - delta_meter_balance[n][t]), \
					'Check_meter_deficit_' + increment

				# Eq. 37
				self.milp += \
					e_sale[n][t] >= - e_cmet[n][t] - self._big_m * (
								1 - delta_meter_balance[n][t] + delta_rec_balance[t]), \
					'Share_all_surplus_low_' + increment

				# Eq. 38
				self.milp += \
					e_sale[n][t] <= - e_cmet[n][t] + self._big_m * (
								1 - delta_meter_balance[n][t] + delta_rec_balance[t]), \
					'Share_all_surplus_high_' + increment

				# Eq. 39
				self.milp += \
					e_pur[n][t] >= e_cmet[n][t] - self._big_m * (
							1 - delta_rec_balance[t] + delta_meter_balance[n][t]), \
					'Buy_all_deficit_low_' + increment

				# Eq. 40
				self.milp += \
					e_pur[n][t] <= e_cmet[n][t] + self._big_m * (
							1 - delta_rec_balance[t] + delta_meter_balance[n][t]), \
					'Buy_all_deficit_high_' + increment

		# Write MILP to .lp file
		dir_name = os.path.abspath(os.path.join(__file__, '..'))
		lp_file = os.path.join(dir_name, f'Stage2Pool.lp')
		self.milp.writeLP(lp_file)

		# Set the solver to be called
		if self.solver == 'CBC' and 'PULP_CBC_CMD' in listSolvers(onlyAvailable=True):
			self.milp.setSolver(pulp.PULP_CBC_CMD(msg=False, timeLimit=self.timeout, gapRel=self.mipgap))

		elif self.solver == 'CPLEX' and 'CPLEX_CMD' in listSolvers(onlyAvailable=True):
			self.milp.setSolver(CPLEX_CMD(msg=True, timeLimit=self.timeout, gapRel=self.mipgap))

		else:
			raise ValueError(f'{self.solver}_CMD not available in puLP; '
			                 f'please install the required solver or try a different one')

		logger.debug('-- defining the collective (pool) MILP problem... DONE!')

		return

	def solve_milp(self):
		"""
		Function that heads the definition and solution of the second stage MILP.
		"""
		# Define the MILP
		self.__define_milp()

		# Solve the MILP
		logger.debug('-- solving the collective (pool) MILP problem...')

		try:
			self.milp.solve()
			status = LpStatus[self.milp.status]
			opt_value = value(self.milp.objective)

		except Exception as e:
			logger.warning(f'Solver raised an error: \'{e}\'. Considering problem as "Infeasible".')
			status = 'Infeasible'
			opt_value = None

		self.status = status
		self.obj_value = opt_value

		logger.debug('-- solving the collective (pool) MILP problem... DONE!')

		return

	def generate_outputs(self) -> OutputsCollectivePoolDict:
		"""
		Function for generating the outputs of optimization, namely the battery's set points.
		:return: outputs dictionary with MILP variables' and other computed values
		"""
		logger.debug('-- generating outputs from the collective (pool) MILP problem...')

		outputs = {}

		# -- Verification added to avoid raising error whenever encountering a puLP solver error with CBC
		if self.obj_value is None:
			return outputs

		outputs['obj_value'] = round(self.obj_value, 3)
		outputs['milp_status'] = self.status

		outputs['p_cont'] = {meter_id: None for meter_id in self.set_meters}
		outputs['p_gn_new'] = {meter_id: None for meter_id in self.set_meters}
		outputs['p_gn_total'] = {meter_id: None for meter_id in self.set_meters}
		outputs['e_bn_new'] = {meter_id: None for meter_id in self.set_meters}
		outputs['e_bn_total'] = {meter_id: None for meter_id in self.set_meters}

		outputs['e_cmet'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['e_g'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['e_bc'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['e_bd'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['e_sup'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['e_sur'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['e_pur_pool'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['e_sale_pool'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['e_slc_pool'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['delta_bc'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['e_bat'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['delta_sup'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['e_consumed'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['e_alc'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['delta_slc'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['delta_cmet'] = dict_none_lists(self.time_intervals, self.set_meters)
		outputs['delta_alc'] = dict_none_lists(self.time_intervals, self.set_meters)
		if self.strict_pos_coeffs:
			outputs['delta_coeff'] = dict_none_lists(self.time_intervals, self.set_meters)
		if self.total_share_coeffs:
			outputs['delta_rec_balance'] = none_lists(self.time_intervals)
			outputs['delta_meter_balance'] = dict_none_lists(self.time_intervals, self.set_meters)

		# required when vars include "-" since puLP converts it to "_"
		matchd = {key: key.replace('-', '_') for key in self.set_meters}
		rematchd = {v: k for k, v in matchd.items()}
		var_name = lambda v_str, n_str: rematchd[v_str.split(n_str)[-1]]

		for v in self.milp.variables():
			if re.search('dummy', v.name):
				continue
			elif re.search('p_cont_', v.name):
				n = var_name(v.name, 'p_cont_')
				outputs['p_cont'][n] = v.varValue
			elif re.search('p_gn_new_', v.name):
				n = var_name(v.name, 'p_gn_new_')
				outputs['p_gn_new'][n] = v.varValue
			elif re.search('p_gn_total_', v.name):
				n = var_name(v.name, 'p_gn_total_')
				outputs['p_gn_total'][n] = v.varValue
			elif re.search('e_bn_new_', v.name):
				n = var_name(v.name, 'e_bn_new_')
				outputs['e_bn_new'][n] = v.varValue
			elif re.search('e_bn_total_', v.name):
				n = var_name(v.name, 'e_bn_total_')
				outputs['e_bn_total'][n] = v.varValue

			else:
				step_nr = int(v.name[-3:])
				v_name_reduced = v.name[:-5]  # var name without step_nr, i.e., without "_t000"

				if re.search(f'delta_rec_balance_', v.name):
					outputs['delta_rec_balance'][step_nr] = v.varValue

				elif re.search(f'e_cmet_', v.name):
					n = var_name(v_name_reduced, 'e_cmet_')
					outputs['e_cmet'][n][step_nr] = v.varValue
				elif re.search(f'e_g_', v.name):
					n = var_name(v_name_reduced, 'e_g_')
					outputs['e_g'][n][step_nr] = v.varValue
				elif re.search(f'e_bc_', v.name):
					n = var_name(v_name_reduced, 'e_bc_')
					outputs['e_bc'][n][step_nr] = v.varValue
				elif re.search(f'e_bd_', v.name):
					n = var_name(v_name_reduced, 'e_bd_')
					outputs['e_bd'][n][step_nr] = v.varValue
				elif re.search(f'e_sup_', v.name):
					n = var_name(v_name_reduced, 'e_sup_')
					outputs['e_sup'][n][step_nr] = v.varValue
				elif re.search(f'e_sur_', v.name):
					n = var_name(v_name_reduced, 'e_sur_')
					outputs['e_sur'][n][step_nr] = v.varValue
				elif re.search(f'e_pur_', v.name):
					n = var_name(v_name_reduced, 'e_pur_')
					outputs['e_pur_pool'][n][step_nr] = v.varValue
				elif re.search(f'e_sale_', v.name):
					n = var_name(v_name_reduced, 'e_sale_')
					outputs['e_sale_pool'][n][step_nr] = v.varValue
				elif re.search(f'e_slc_', v.name):
					n = var_name(v_name_reduced, 'e_slc_')
					outputs['e_slc_pool'][n][step_nr] = v.varValue
				elif re.search(f'delta_bc_', v.name):
					n = var_name(v_name_reduced, 'delta_bc_')
					outputs['delta_bc'][n][step_nr] = v.varValue
				elif re.search(f'e_bat_', v.name):
					n = var_name(v_name_reduced, 'e_bat_')
					outputs['e_bat'][n][step_nr] = v.varValue
				elif re.search(f'delta_sup_', v.name):
					n = var_name(v_name_reduced, 'delta_sup_')
					outputs['delta_sup'][n][step_nr] = v.varValue
				elif re.search(f'e_consumed_', v.name):
					n = var_name(v_name_reduced, 'e_consumed_')
					outputs['e_consumed'][n][step_nr] = v.varValue
				elif re.search(f'e_alc_', v.name):
					n = var_name(v_name_reduced, 'e_alc_')
					outputs['e_alc'][n][step_nr] = v.varValue
				elif re.search(f'delta_slc_', v.name):
					n = var_name(v_name_reduced, 'delta_slc_')
					outputs['delta_slc'][n][step_nr] = v.varValue
				elif re.search(f'delta_cmet_', v.name):
					n = var_name(v_name_reduced, 'delta_cmet_')
					outputs['delta_cmet'][n][step_nr] = v.varValue
				elif re.search(f'delta_alc_', v.name):
					n = var_name(v_name_reduced, 'delta_alc_')
					outputs['delta_alc'][n][step_nr] = v.varValue
				elif re.search(f'delta_coeff_', v.name):
					n = var_name(v_name_reduced, 'delta_coeff_')
					outputs['delta_coeff'][n][step_nr] = v.varValue
				elif re.search(f'delta_meter_balance', v.name):
					n = var_name(v_name_reduced, 'delta_meter_balance_')
					outputs['delta_meter_balance'][n][step_nr] = v.varValue

		# Include other individual cost metrics

		outputs['c_ind2pool'] = {n: None for n in self.set_meters}
		for n in self.set_meters:
			e_sup = np.array(outputs['e_sup'][n])
			l_buy = np.array(self._l_buy[n])
			e_sur = np.array(outputs['e_sur'][n])
			l_sell = np.array(self._l_sell[n])
			e_slc = np.array(outputs['e_slc_pool'][n])
			l_grid = np.array(self._l_grid)
			p_cont = outputs['p_cont'][n]
			l_cont = self._l_cont[n]
			p_gn_new = outputs['p_gn_new'][n]
			l_gic = self._l_gic[n]
			e_bn_new = outputs['e_bn_new'][n]
			l_bic = self._l_bic[n]

			c_ind_array = sum(e_sup * l_buy - e_sur * l_sell + e_slc * l_grid) + \
			              p_cont * l_cont * self._nr_days + \
			              p_gn_new * l_gic * self._nr_days + \
			              e_bn_new * l_bic * self._nr_days
			outputs['c_ind2pool'][n] = round(c_ind_array, 3)

		# Also retrieve the slack values of the "Market Equilibrium" constraints. These can be considered as the
		# "optimal" market prices.
		dual_prices = \
			[abs(self.milp.constraints[c].pi) for c in self.milp.constraints if c.startswith('Market_equilibrium_')]
		outputs['dual_prices'] = [round(dp, 4) for dp in dual_prices]

		logger.debug('-- generating outputs from the collective (pool) MILP problem... DONE!')

		return outputs
