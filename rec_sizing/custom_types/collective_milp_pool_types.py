from rec_sizing.custom_types.meters_types import Meters
from typing import (
	TypeAlias,
	TypedDict
)


# -- INPUTS ------------------------------------------------------------------------------------------------------------
class BackpackCollectivePoolDict(TypedDict):
	nr_days: float
	l_grid: list[float]
	delta_t: float
	storage_ratio: float
	strict_pos_coeffs: bool
	sum_one_coeffs: bool
	meters: Meters


# -- OUTPUTS -----------------------------------------------------------------------------------------------------------
ValuePerId: TypeAlias = dict[
	str, float
]

ListPerId: TypeAlias = dict[
	str, list[float]
]

ListPerIdPerId: TypeAlias = dict[
	str, ListPerId
]


class OutputsCollectivePoolDict(TypedDict):
	c_ind2pool: ValuePerId
	c_ind2pool_without_p_extra: ValuePerId
	delta_alc: ListPerId
	delta_cmet: ListPerId
	delta_coeff: ListPerId
	delta_slc: ListPerId
	delta_sup: ListPerId
	dual_prices: list[float]
	e_alc: ListPerId
	e_cmet: ListPerId
	e_consumed: ListPerId
	e_pur_pool: ListPerId
	e_sale_pool: ListPerId
	e_slc_pool: ListPerId
	e_sup_market: ListPerId
	e_sup_retail: ListPerId
	e_sur_market: ListPerId
	e_sur_retail: ListPerId
	milp_status: str
	obj_value: float
	p_extra: ListPerId
	p_extra_cost2pool: ValuePerId
	c_ind2pool_without_deg: ValuePerId
	c_ind2pool_without_deg_and_p_extra: ValuePerId
	deg_cost2pool: ValuePerId
	delta_bc: ListPerIdPerId
	e_bat: ListPerIdPerId
	e_bc: ListPerIdPerId
	e_bd: ListPerIdPerId
	soc_bat: ListPerIdPerId
