from . import core as c
from . import transform as t
from . import db
from . import active_retention_date

def api2db(api_spec, db_spec, db_table_name, custom_params, maxrows=None):
  sess = c.make_authed_session_obj(api_spec)
  api_dataset = c.get_records(api_spec, sess, custom_params, maxrows)
  hp_rows = list(map(t.into_hp_row, api_dataset))

  # drop/recreate table
  db.db_drop_table(
    db_spec,
    db.db_schema_name_from_fqtn(db_table_name),
    db.db_table_from_fqtn(db_table_name))
  with open('sql/create-table.sql') as f:
    ddl = f.read()
    db.db_stmt(db_spec, ddl.replace('$TABLE_NAME$', db_table_name))

  # We just recreated table, reintroduce calculated column(s).
  active_retention_date.add_column_if_needed(db_spec, db_table_name)

  # Active Retention Date calculated field.
  for row in hp_rows:
    art = active_retention_date.calc_val(row)
    row[active_retention_date.COLUMN_NAME] = art

  # Insert finished dataset.
  result = db.db_insert_many(db_spec, db_table_name, hp_rows)
  return result

