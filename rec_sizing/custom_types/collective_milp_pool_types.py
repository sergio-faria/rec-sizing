from rec_sizing.custom_types.meters_types import Meters
from typing import (
	TypeAlias,
	TypedDict,
	Union
)


# -- INPUTS ------------------------------------------------------------------------------------------------------------
class BackpackCollectivePoolDict(TypedDict):
	nr_days: int
	nr_clusters: int
	l_grid: list[float]
	delta_t: float
	storage_ratio: float
	strict_pos_coeffs: bool
	total_share_coeffs: bool
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
	obj_value: float
	milp_status: str
	p_cont: ValuePerId
	p_gn_new: ValuePerId
	p_gn_total: ValuePerId
	e_bn_new: ValuePerId
	e_bn_total: ValuePerId
	e_cmet: ListPerId
	e_g: ListPerId
	e_bc: ListPerIdPerId
	e_bd: ListPerIdPerId
	e_sup: ListPerId
	e_sur: ListPerId
	e_pur_pool: ListPerId
	e_sale_pool: ListPerId
	e_slc_pool: ListPerId
	e_bat: ListPerIdPerId
	delta_sup: ListPerId
	e_consumed: ListPerId
	e_alc: ListPerId
	delta_slc: ListPerId
	delta_coeff: ListPerId
	delta_rec_balance: list[float]
	delta_meter_balance: ListPerId
	c_ind2pool: ValuePerId
	dual_prices: list[float]
