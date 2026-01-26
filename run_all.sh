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

echo "[$(date +'%Y-%m-%d %H:%M:%S')] try removing existing data"

rm_tqdb huxiaoou_private --table sector_c0_d
python main.py c0 --bgn $bgn_date --end $end_date --freq d

rm_tqdb huxiaoou_private --table sector_c0_m
python main.py c0 --bgn $bgn_date --end $end_date --freq m
