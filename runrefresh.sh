#!/bin/sh
# Example to run at 5 am each day: 
# 00 5 * * * /home/ras3005/boost/aourefresh/runrefresh.sh > /dev/null
cd "$(dirname "${BASH_SOURCE[0]}")"
source ./venv/bin/activate && python ./refresh.py --site-config enclave/site-config-columbia.json --aou-api-spec enclave/aou-api-spec.json --db-spec enclave/p04.json
source ./venv/bin/activate && python ./refresh.py --site-config enclave/site-config-harlem.json --aou-api-spec enclave/aou-api-spec.json --db-spec enclave/p04.json
source ./venv/bin/activate && python ./refresh.py --site-config enclave/site-config.json --aou-api-spec enclave/aou-api-spec.json --db-spec enclave/p04.json
cd ../aoupostproc/
source ./venv/bin/activate && hy ./aoupostproc.hy p04

