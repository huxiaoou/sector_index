#!/usr/bin/bash -l

proj_dir=/root/workspace/Projects/sector_index

ch=$(date +"%H")
if [ $ch -ge "14" ] &&  [ $ch -lt "15" ]; then
    cd $proj_dir
    pwd
    ./run_daily_increment.sh --auto
else
    tt=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[INF] $tt Wrong hour for cal signals"
fi