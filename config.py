import yaml
from qtools_sxzq.qdata import CDataDescriptor
from typedef import TLevel, TName, TSector, TInstrument
from typedef import CCfgDbs, CCfgIndexBase, CSectorClassification, TClassifications
from typedef import CCfg

with open("config.yaml", "r") as f:
    _config = yaml.safe_load(f)

d: TClassifications = {}
for level, level_data in _config["classification"].items():
    level: TLevel
    level_data: dict
    for name, name_data in level_data.items():
        name: TName
        name_data: dict[TSector, list[TInstrument]]
        d[name] = CSectorClassification(level=level, name=name, data=name_data)

cfg = CCfg(
    dbs=CCfgDbs(**_config["dbs"]),
    path_calendar=_config["path_calendar"],
    index_base=CCfgIndexBase(**_config["index_base"]),
    classifications=d,
)

"""
-------------------
--- public data ---
-------------------
"""

data_desc_pv = CDataDescriptor(codes=[], **_config["src_tables"]["pv"])
data_desc_pv1m = CDataDescriptor(codes=[], **_config["src_tables"]["pv1m"])

if __name__ == "__main__":
    print(cfg)
    print(data_desc_pv)
    print(data_desc_pv1m)
