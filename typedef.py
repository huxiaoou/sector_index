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


TFreq = Literal["d", "m", None]
TName = str
TSector = str
TInstrument = str
TClsData = dict[TSector, list[TInstrument]]
TInstruMap = dict[TInstrument, TSector]


@dataclass(frozen=True)
class CSectorClassification:
    name: TName  # ["c0", "c1", ...]
    data: TClsData

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

    def get_save_data_desc(self, db_name: str, freq: TFreq) -> CDataDescriptor:
        return CDataDescriptor(
            db_name=db_name,
            table_name=f"sector_{self.name}_{freq}",
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
