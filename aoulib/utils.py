import os
import logging
from logging.handlers import RotatingFileHandler
from email.message import EmailMessage
import smtplib 
import json
import datetime

def slurpj(fname):
  with open(fname) as f:
    return json.load(f)

def spit(fname, bytes):
  with open(fname, 'wb') as f:
    f.write(bytes)

def smart_logger(tag='default', logdir='./log', __cache__={}):
    if not tag:
        raise ValueError('tag needs to be a non-empty string')
    # make logdir if needed
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    # return pre-existing logger if exists
    if tag in __cache__:
        return __cache__[tag]
    else:
        x = logging.getLogger(tag)
        x.setLevel(logging.INFO)
        logpath = logdir + os.path.sep + tag + '.log'
        handler = RotatingFileHandler(logpath,
                                      maxBytes=33554432,
                                      backupCount=16)
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] '
                                '[%(filename)s:%(lineno)s %(funcName)s] '
                                '%(message)s')
        handler.setFormatter(fmt)
        x.addHandler(handler)
        __cache__[tag] = x
        return x

def send_email(*, frm=None, to=None, subj=None, body=None):
    em = EmailMessage()
    em['From'] = frm
    em['To'] = to
    em['Subject'] = subj
    em.set_content(body)
    s = smtplib.SMTP('localhost')
    s.send_message(em)
    s.quit()

def today_as_str():
  '''Current date as a string: yyyy-mm-dd'''
  return datetime.date.today().strftime("%Y-%m-%d")

