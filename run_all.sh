#!/usr/bin/bash -l

if [ "$#" -eq 1 ]; then
    if [ "$1" = "--auto" ]; then
        end_date=$(date +"%Y%m%d")
    else
        end_date="$1"
    fi
else
    read -p "Please input the end date, format = [YYYYMMDD]:" end_date
fi
echo "end_date = $end_date"
bgn_date="20180102"


cls="c2"
echo "[$(date +'%Y-%m-%d %H:%M:%S')] try to remove existed database"
udb=$(python -c $'import yaml\nwith open("config.yaml", "r") as f:_config = yaml.safe_load(f)\nprint(_config["dbs"]["user"])')
echo "user_db=$udb"
rm_tqdb $udb --table sector_index_${cls}_weights
rm_tqdb $udb --table sector_index_${cls}_d
rm_tqdb $udb --table sector_index_${cls}_m
python main.py $cls --bgn $bgn_date --end $end_date --weights
python main.py $cls --bgn $bgn_date --end $end_date --freq d
python main.py $cls --bgn $bgn_date --end $end_date --freq m
