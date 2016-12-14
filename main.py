from app import app
from view import *

import logging.config
from logging.handlers import RotatingFileHandler
from logging import Formatter

LOGFILE='/var/log/wq_rest/flask_plug_view_site.log'

def init_logging():
  file_handler = RotatingFileHandler(filename = LOGFILE)
  file_handler.setLevel(logging.DEBUG)
  file_handler.setFormatter(Formatter('''
  Message type:       %(levelname)s
  Location:           %(pathname)s:%(lineno)d
  Module:             %(module)s
  Function:           %(funcName)s
  Time:               %(asctime)s

  Message:

  %(message)s
  '''))
  app.logger.addHandler(file_handler)
  #logging.config.fileConfig(LOGCONFFILE)
  #logger = logging.getLogger('wq_rest_logger')
  #logger.info("Log file opened")
  #wq_app.logger = logging.getLogger('wq_rest_logger')
  return

if __name__ == '__main__':
  init_logging()
  app.run(debug=True)
