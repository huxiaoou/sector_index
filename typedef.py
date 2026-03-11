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
TInstruMap = dict[TSector, dict[TInstrument, int]]


@dataclass(frozen=True)
class CSectorClassification:
    name: TName  # ["c0", "c1", ...]
    data: TClsData

    def comb_name(self, freq: TFreq) -> str:
        return f"{self.name}_{freq}"

    @property
    def instru_map(self) -> TInstruMap:
        res: TInstruMap = {}
        for sector, instruments in self.data.items():
            sector: TSector
            instruments: list[TInstrument]
            res[sector] = {ins: 1 for ins in instruments}
        return res

    @property
    def sectors(self) -> list[str]:
        return sorted(list(self.data))

    @property
    def codes(self) -> list[str]:
        res: set[str] = set()
        for instruments in self.data.values():
            res = res.union(set(instruments))
        return sorted(list(res))

    def get_save_data_desc(self, db_name: str, freq: TFreq) -> CDataDescriptor:
        return CDataDescriptor(
            db_name=db_name,
            table_name=f"sector_index_{self.comb_name(freq)}",
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

    def __post_init__(self):
        seen: set[str] = set()
        for cls_name, clsf in self.classifications.items():
            for sector in clsf.sectors:
                if sector in seen:
                    raise ValueError(
                        f"Duplicate sector id '{sector}' found in classification '{cls_name}'; "
                        f"sector ids must be unique across all classifications."
                    )
                seen.add(sector)
