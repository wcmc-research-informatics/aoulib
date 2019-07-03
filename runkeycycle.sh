SHELL=/bin/bash
# Example to run at 4 am each day: 
# 00 4 * * * ~/boost/aourefesh/runkeycycle.sh > /dev/null
cd /home/ras3005/boost/aourefresh
source /home/ras3005/boost/aourefresh/venv/bin/activate && python /home/ras3005/boost/aourefresh/keycycle.py --site-config enclave/site-config.json --aou-api-spec enclave/aou-api-spec.json

