from typing import (
	TypeAlias,
	TypedDict,
	Union
)


class SingleBTMEVs(TypedDict):
	trip_ev: list[float]
	min_energy_storage_ev: float
	battery_capacity_ev: float
	eff_bc_ev: float
	eff_bd_ev: float
	init_e_ev: float
	pmax_c_ev: float
	pmax_d_ev: float
	bin_ev: list[int]


BTMEVs:	TypeAlias = dict[
	str, SingleBTMEVs
]


class EWHSpecs(TypedDict):
	ewh_capacity: float
	ewh_power: float
	ewh_max_temp: float
	user_comf_temp: float
	tariff: float
	price_simple: float
	price_dual_day: float
	price_dual_night: float
	tariff_simple: float
	tariff_dual: float


class ParamsInput(TypedDict):
	user: str
	datetime_start: str
	datetime_end: str
	load_diagram_exists: int
	ewh_specs: EWHSpecs


class Dataset(TypedDict):
	start: list[str]
	duration: list[int]


class SingleEWH(TypedDict):
	params_input: ParamsInput
	dataset: Dataset


EWH: TypeAlias = dict[
	str, SingleBTMEVs
]


class SingleMeter(TypedDict):
	l_buy: list[float]
	l_sell: list[float]
	l_cont: float
	l_gic: float
	l_bic: float
	e_c: list[float]
	p_gn_init: float
	e_g_factor: list[float]
	p_gn_min: float
	p_gn_max: float
	e_bn_init: float
	e_bn_min: float
	e_bn_max: float
	soc_min: float
	eff_bc: float
	eff_bd: float
	soc_max: float
	btm_evs: Union[BTMEVs, None]
	ewh: Union[EWH, None]


Meters: TypeAlias = dict[
	str, SingleMeter
]
