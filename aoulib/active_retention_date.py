import datetime
from dateutil import parser
from .db import *

COLUMN_NAME = 'Active Retention Date'

def str2date(x):
    if x.strip() == '':
        x = '1900-01-01'
    return parser.parse(x).date()

def calc_val(rcd):
    '''
    Returns either:
      * a string containing a date representation formatted like 'YYYY-MM-DD'.
      * an empty string

    The critera are as follows:
    
        1) Filter:
        
        retentionEligibleStatus = 1 
        AND (
            completed any of the following surveys in the 
            last 547 days:
                - PPI4 - Healthcare Access PPI Module
                - PPI5 - Family Health PPI Module
                - PPI6 - Medical History PPI Module
                - PPI7 - COPE PPI Module (May, June, or July) 
            )

        2) The field should return the **earliest date** between
        547 days ago and today, inclusive, amongst all the  
        pertinent date items above.

        3) If the criteria above are not met, then the
        empty string will be returned. 

    '''
    # Identify values of interest for calculation.
    retention_status    = rcd['retentionEligibleStatus']
    # PPI4 - Healthcare Access PPI Module
    access_ppi          = rcd['Access PPI Survey Complete']
    access_ppi_dt       = str2date(rcd['Access PPI Survey Completion Date'])
    # Family Health PPI Module
    fam_ppi             = rcd['Family PPI Survey Complete']
    fam_ppi_dt          = str2date(rcd['Family PPI Survey Completion Date'])
    # PPI6 - Medical History PPI Module 
    hist_ppi            = rcd['Hist PPI Survey Complete']
    hist_ppi_dt         = str2date(rcd['Hist PPI Survey Completion Date'])
    # PPI7 - COPE PPI Module (May, June, or July)
    cope_may        = rcd['COPE May PPI Survey Complete']
    cope_may_dt     = str2date(rcd['COPE May PPI Survey Completion Date'])
    cope_june       = rcd['COPE June PPI Survey Complete']
    cope_june_dt    = str2date(rcd['COPE June PPI Survey Completion Date'])
    cope_july       = rcd['COPE July PPI Survey Complete']
    cope_july_dt    = str2date(rcd['COPE July PPI Survey Completion Date'])

    # Determine what date 547 days ago was.
    begin_dt = datetime.datetime.now().date() - datetime.timedelta(days=547)

    # List of potential destination values; we'll resolve to
    # one of these to return (if we don't return the empty string).
    potentials = []

    # 1) Determine if we return date, or empty string.
    if retention_status == 'ELIGIBLE':
        if (access_ppi == '1' and access_ppi_dt >= begin_dt):
            potentials.append(access_ppi_dt)
        if (fam_ppi == '1' and fam_ppi_dt >= begin_dt):
            potentials.append(fam_ppi_dt)
        if (hist_ppi == '1' and hist_ppi_dt >= begin_dt):
            potentials.append(hist_ppi_dt)
        if (cope_may == '1' and cope_may_dt >= begin_dt):
            potentials.append(cope_may_dt)
        if (cope_june == '1' and cope_june_dt >= begin_dt):
            potentials.append(cope_june_dt)
        if (cope_july == '1' and cope_july_dt >= begin_dt):
            potentials.append(cope_july_dt)

    # At this point return empty string when it makes sense to
    # do so.
    if potentials == []: return ''

    # 2) determine which data
    out = min(potentials)

    # 3) convert into required str format.
    out = out.strftime("%Y-%m-%d")

    # All set; return prepped string. 
    return out

#------------------------------------------------------------------------------
# db 

def add_column_if_needed(db_spec, db_table_name):
    '''
    Get column names.
    If 'Active Retention Date' isn't there, add it to the table.
    '''
    catalog, schema, table = db_table_name.split('.')
    # Add 'database' key to db_spec; needed for operations here.
    db_spec = db_spec.copy()
    db_spec['database'] = catalog
    # Get current column names.
    cols = [row['column_name'] 
            for row in db_get_table_info(db_spec, schema, table)]
    if COLUMN_NAME not in cols:
        # Column doesn't exist; add it.
        stmt = ('alter table [{}].[{}] add [{}] [nvarchar](32) NULL'
                ''.format(schema, table, COLUMN_NAME))
        db_stmt(db_spec, stmt)

