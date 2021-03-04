aoulib
------

The `aoulib` Python library provides functions for working efficiently with the AoU Data Ops API. It's designed to be used in a REPL or imported into an application. You can use this format in your requirements.txt file:

    aoulib @ git+https://github.com/wcmc-research-informatics/aoulib/#egg=aoulib

It also comes with two Python modules useful for automating data transfer and key cycling:

* `refresh.py` and `runrefresh.sh` facilitate automated refreshing of data from the AoU Data Ops API to a local SQL Server database table.
* `keycycle.py` and `runkeycycle.sh` facilitate automated creation and deletion of GCP service account keys and updating of a local key file.
* See comments in `refresh.py` and `keycycle.py` for details about setup and configuration.
 
Additional notes:  

* If you need to test your AoU Data Ops API connectivity at a basic level, see the script in the `apitest` folder.
* Targets Python 3.9.0

Useful gcloud commands:

* gcloud iam service-accounts keys list --iam-account service-account-name-goes-here
* gcloud iam service-accounts keys create key.json --iam-account service-account-name-goes-here

## Release Notes

* March 2021:
    - the destination database table is now dropped and recreated each
      time `transform.api2db` runs;
    - additional fields included, mainly those pertinent to lab data.

