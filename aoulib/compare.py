import sqlsrvwrapper as s
import kickshaws as ks

'''
Example usage:
>>> import compare
>>> compare(db_spec, 'dm_aou..healthpro', 'dm_aou..healthpro2')
'''

def select_row(dataset, pmi_id):
  for mp in dataset:
    if mp['PMI ID'] == pmi_id:
      return mp
  return None

def extract_ids(dataset):
  return [row['PMI ID'] for row in dataset]

def comp(d1, d2):
  out = ''
  d1_ids = extract_ids(d1)
  d2_ids = extract_ids(d2)
  for id in d1_ids:
    d1_row = select_row(d1, id)
    d2_row = select_row(d2, id)
    if d2_row:
      diff = {k: d2_row[k] for k in d2_row if k in d1_row and d2_row[k] != d1_row[k]}
      if diff:
        diffstr = id + '\t\t\t' + str(diff) + '\n'
        out += diffstr
  return out

def go(db_spec, t1, t2):
  d1 = s.db_qy(db_spec, 'select * from ' + t1)
  d2 = s.db_qy(db_spec, 'select * from ' + t2)
  rslt = comp(d1, d2)
  print rslt

