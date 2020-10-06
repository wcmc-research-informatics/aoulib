from . import core as c
from . import transform as t
from . import db
import active_retention_date

def api2db(api_spec, db_spec, db_table_name, custom_params, maxrows=None):
  sess = c.make_authed_session_obj(api_spec)
  api_dataset = c.get_records(api_spec, sess, custom_params, maxrows)
  hp_rows = list(map(t.into_hp_row, api_dataset))

  # Active Retention Date calculated field.
  active_retention_date.add_column_if_needed(db_spec, db_table_name)
  for row in hp_rows:
    art = active_retention_date.calc_val(row)
    row[active_retention_date.COL_NAME] = art

  db.db_trunc_table(db_spec, db_table_name)
  result = db.db_insert_many(db_spec, db_table_name, hp_rows)
  return result

