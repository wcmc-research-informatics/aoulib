from __future__ import division
from __future__ import print_function
import core as c
import transform as t
import sqlsrvwrapper as s

def api2db(api_spec, db_spec, db_table_name, custom_params, maxrows):
  sess = c.make_authed_session(api_spec['path-to-key-file'])
  api_dataset = c.get_records(api_spec, sess, custom_params, maxrows)
  hp_rows = map(t.into_hp_row, api_dataset)
  s.db_trunc_table(db_spec, db_table_name)
  result = s.db_insert_many(db_spec, db_table_name, hp_rows)
  return result

