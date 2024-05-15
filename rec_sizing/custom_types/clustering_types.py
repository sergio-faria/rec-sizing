from typing import (
	Dict,
	List,
	TypeAlias,
	TypedDict
)


# -- INPUTS ------------------------------------------------------------------------------------------------------------
class TimeseriesDataDict(TypedDict):
	e_g_factor: List[float]
	e_c: List[float]
	l_buy: List[float]
	l_sell: List[float]


class BackpackKMedoids(TypedDict):
	nr_days: int
	delta_t: float
	nr_representative_days: int
	l_grid: List[float]
	timeseries_data: Dict[str, TimeseriesDataDict]


# -- OUTPUTS -----------------------------------------------------------------------------------------------------------
CommonRepresentativeTimeseriesDict: TypeAlias = Dict[str, Dict[str, List[float]]]


class OutputsKMedoids(TypedDict):
	inertia: float
	cluster_labels: List[str]
	representative_e_g_factor: CommonRepresentativeTimeseriesDict
	representative_e_c: CommonRepresentativeTimeseriesDict
	representative_l_buy: CommonRepresentativeTimeseriesDict
	representative_l_sell: CommonRepresentativeTimeseriesDict
	representative_l_grid: Dict[str, List[float]]
	cluster_nr_days: Dict[str, float]
