import yaml
from typedef import TLevel, TName, TSector, TInstrument
from typedef import CCfgIndexBase, CSectorClassification, TClassifications
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
    path_calendar=_config["path_calendar"],
    index_base=CCfgIndexBase(**_config["index_base"]),
    classifications=d,
)

if __name__ == "__main__":
    print(cfg)
