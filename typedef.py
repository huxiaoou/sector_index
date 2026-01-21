from dataclasses import dataclass
from typing import Literal
from qtools_sxzq.qdata import CDataDescriptor


@dataclass(frozen=True)
class CCfgDbs:
    public: str
    user: str


@dataclass(frozen=True)
class CCfgIndexBase:
    date: str
    value: float


TLevel = Literal["LEVEL1", "LEVEL2"]
TName = str
TSector = str
TInstrument = str
TInstruMap = dict[TInstrument, TSector]


@dataclass(frozen=True)
class CSectorClassification:
    level: TLevel
    name: TName  # ["CA00", "CA01", "CB00", ...]
    data: dict[TSector, list[TInstrument]]

    @property
    def instru_map(self) -> TInstruMap:
        res: TInstruMap = {}
        for sector, instruments in self.data.items():
            for instrument in instruments:
                res[instrument] = sector
        return res

    @property
    def sectors(self) -> list[str]:
        return sorted(list(self.data))

    @property
    def codes(self) -> list[str]:
        res: list[str] = []
        for instruments in self.data.values():
            res.extend(instruments)
        return res

    def save_table(self, db_name: str) -> CDataDescriptor:
        return CDataDescriptor(
            db_name=db_name,
            table_name=f"sector_{self.level}_{self.name}",
            codes=self.sectors,
            fields=["ret", "close"],
            lag=20,
            data_view_type="data3d",
        )


TClassifications = dict[TName, CSectorClassification]


@dataclass(frozen=True)
class CCfg:
    dbs: CCfgDbs
    path_calendar: str
    index_base: CCfgIndexBase
    classifications: TClassifications
