#!/bin/sh
# Example to run at 4 am each day: 
# 00 4 * * * /home/ras3005/boost/aourefresh/runkeycycle.sh > /dev/null
cd "$(dirname "${BASH_SOURCE[0]}")"
source ./venv/bin/activate && python ./keycycle.py --site-config enclave/site-config.json --aou-api-spec enclave/aou-api-spec.json

