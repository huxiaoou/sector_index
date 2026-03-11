#!/usr/bin/bash -l

udb=$(python -c $'import yaml\nwith open("config.yaml", "r") as f:_config = yaml.safe_load(f)\nprint(_config["dbs"]["user"])')
echo "user_db=$udb"

cls="c2"
bgn="20180102"
end="20260310"

rm_tqdb $udb --table sector_index_${cls}_weights
rm_tqdb $udb --table sector_index_${cls}_d
rm_tqdb $udb --table sector_index_${cls}_m

python main.py $cls --bgn $bgn --end $end --weights
python main.py $cls --bgn $bgn --end $end --freq d
python main.py $cls --bgn $bgn --end $end --freq m
