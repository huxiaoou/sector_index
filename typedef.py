from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class CCfgIndexBase:
    date: str
    value: float


TLevel = Literal["LEVEL1", "LEVEL2"]
TName = str
TSector = str
TInstrument = str


@dataclass(frozen=True)
class CSectorClassification:
    level: TLevel
    name: TName  # ["CA00", "CA01", "CB00", ...]
    data: dict[TSector, list[TInstrument]]


TClassifications = dict[TName, CSectorClassification]


@dataclass(frozen=True)
class CCfg:
    path_calendar: str
    index_base: CCfgIndexBase
    classifications: TClassifications
