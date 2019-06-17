
### Setup

    mkdir venv
    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements.txt --upgrade --upgrade-strategy eager

### Running refresh.py

#### Database specification

Create a file named `enclave/db-spec.json` with the contents:

    {"host": "X"
    ,"user": "X" 
    ,"password": "X"}

### Provisos

* Uses `US/Eastern` timezone for conversions. Change this in `mapping.py` if desired.

