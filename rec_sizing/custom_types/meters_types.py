from typing import Dict, List, TypedDict, Union
# If you prefer to keep the 'TypeAlias' name, uncomment the next line and install typing-extensions
# from typing_extensions import TypeAlias

class SingleMeter(TypedDict):
    l_buy: List[float]
    l_sell: List[float]
    l_cont: float
    l_gic: float
    l_bic: float
    e_c: List[float]
    p_gn_init: float
    e_g_factor: List[float]
    p_gn_min: float
    p_gn_max: float
    e_bn_init: float
    e_bn_min: float
    e_bn_max: float
    soc_min: float
    eff_bc: float
    eff_bd: float
    soc_max: float
    deg_cost: float


# Python 3.8-compatible alias
Meters = Dict[str, SingleMeter]  # type: TypeAlias
