#!/usr/bin/bash -l

if [ "$#" -eq 1 ]; then
    if [ "$1" = "--auto" ]; then
        append_date=$(date +"%Y%m%d")
    else
        append_date="$1"
    fi
else
    read -p "Please input the end date, format = [YYYYMMDD]:" append_date
fi
echo "append_date = $append_date"

python main.py c0 --bgn $append_date --freq d
python main.py c0 --bgn $append_date --freq m
