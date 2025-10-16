from typing import Dict, List, TypedDict, Union
# Optional backport (if you prefer to keep 'TypeAlias'):
# from typing_extensions import TypeAlias


# general_helpers.py
ForecastsList = List[float]  # type: TypeAlias


class SinglePeerMeasuresDict(TypedDict):
    peer_id: str
    measure: float


class SingleUpacMeasuresDict(TypedDict):
    upac_id: str
    measure: float


class PeerMeasuresDict(TypedDict):
    peer_measures: List[SinglePeerMeasuresDict]


class UpacMeasuresDict(TypedDict):
    upac_measures: List[SingleUpacMeasuresDict]


InputDatadict = Union[PeerMeasuresDict, UpacMeasuresDict]  # type: TypeAlias


# milp_helpers.py
MetersDict = Dict[str, Dict[str, List[float]]]  # type: TypeAlias
MetersParamDict = Dict[str, List[float]]  # type: TypeAlias
