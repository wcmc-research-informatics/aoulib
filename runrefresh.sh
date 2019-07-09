#!/bin/sh
# Example to run at 5 am each day: 
# 00 5 * * * /home/ras3005/boost/aourefresh/runrefresh.sh > /dev/null
cd /home/ras3005/boost/aourefresh
source /home/ras3005/boost/aourefresh/venv/bin/activate && python /home/ras3005/boost/aourefresh/refresh.py --site-config enclave/site-config.json --aou-api-spec enclave/aou-api-spec.json --db-spec enclave/p03.json

