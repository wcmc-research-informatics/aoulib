SHELL=/bin/bash
# Example to run at 5 am each day: 
# 00 5 * * * ~/boost/aou-etl/runjob.sh > /dev/null
cd /home/ras3005/boost/aou-etl
source /home/ras3005/boost/aou-etl/venv/bin/activate && python /home/ras3005/boost/aou-etl/refresh.py --aou-api-spec-fpath enclave/aou-api-spec.json --db-spec-fpath enclave/p03.json

