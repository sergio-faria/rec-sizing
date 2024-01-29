from typing import (
	TypeAlias,
	TypedDict
)


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


Meters: TypeAlias = dict[
	str, SingleMeter
]
