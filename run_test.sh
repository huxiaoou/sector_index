#!/usr/bin/bash -l

rm_tqdb huxiaoou_private --table sector_c0_d
echo $(date +"%Y-%m-%d %H:%M:%S")
python main.py c0 --bgn 20180102 --end 20260122 --freq d
echo $(date +"%Y-%m-%d %H:%M:%S")
