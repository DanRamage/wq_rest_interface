from app import app, build_init_db, install_secret_key
import optparse

import logging.config
from logging.handlers import RotatingFileHandler
from logging import Formatter

from config import *



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
  app.logger.debug("Logging initialized")

  return

if __name__ == '__main__':
  parser = optparse.OptionParser()

  parser.add_option("-u", "--User", dest="user",
                    help="User to add", default=None)
  parser.add_option("-p", "--Password", dest="password",
                    help="Stations file to import.", default=None )
  (options, args) = parser.parse_args()

  init_logging()
  if(options.user is not None):
    if(options.password is not None):
      build_init_db(options.user, options.password)
    else:
      print("Must provide password")
  else:
    install_secret_key(app, SECRET_KEY_FILE)
    app.logger.debug("Starting app")
    app.run(debug=FLASK_DEBUG)
