
### Setting up and running refresh.py

#### Requirements

* Known to work with Python 2.7.16 and a modern version of SQL Server.

#### Virtualenv and dependencies

    mkdir venv
    virtualenv -p python2 venv
    source venv/bin/activate
    ./installdeps.sh

#### "enclave" folder 

Create the `enclave` folder for storing specification files

    md enclave

#### AoU API specification file

Create  `enclave/aou-api-spec.json` with these contents:

    {"path-to-key-file": "/path/to/my/key.json",
     "base-url": "https://all-of-us-rdr-prod.appspot.com/rdr/v1/",
     "service-account": "X",
     "awardee": "X"}

_Note:_ please confirm the URL, but the one above will most likely be what you'll use.

#### Database specification file

Create a file named `enclave/db-spec.json` inside `enclave` with the contents:

    {"host": "X",
     "user": "X",
     "password": "X",
     "fully-qualified-table-name", "X"}

This will be used to connect to your SQL Server instance.

#### Run refresh.py 

* If you pass no arguments, then refresh.py will read the aou-api-spec and db-spec files
  that you created and placed in the enclave folder, and proceed to truncate the
  target database table, and then refresh it with a new dataset retrieved via the API. 

* Alternately, you can override those defaults by specifying one or both custom
* spec files on the command line. See optional command-line arguments below.

* Finally, if you wish to conduct a test, you can specify a value for maxrows
  (the program doesn't honor the value exactly but will be close). This way,
  you can test your pipeline and configuration without waiting for an entire dataset
  to load/process.

**Usage details:**

    usage: refresh.py [-h] [--aou-spec AOU_SPEC] [--db-spec DB_SPEC]
                      [--maxrows MAXROWS]

    optional arguments:
      -h, --help           show this help message and exit
      --aou-spec AOU_SPEC  Path to a custom aou-api-spec JSON file.
      --db-spec DB_SPEC    Path to a custom db-spec JSON file.
      --maxrows MAXROWS    Maximum amount of rows to retrieve (approx).

### Provisos

* Uses `US/Eastern` timezone for conversions. Change this in `transform.py` if desired.

