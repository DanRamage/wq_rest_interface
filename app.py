from flask import Flask
import logging.config
import simplejson

from view import *

app = Flask(__name__)
app.debug = True

LOGCONFFILE = '/var/www/wq_rest_interface/wq_rest.conf'
#LOGCONFFILE = '/Users/danramage/Documents/workspace/WaterQuality/wq_rest_interface/wq_rest.conf'

FL_SARASOTA_PREDICTIONS_FILE='/mnt/fl_wq/Predictions.json'
FL_SARASOTA_ADVISORIES_FILE='/mnt/fl_wq/monitorstations/beachAdvisoryResults.json'

SC_MB_PREDICTIONS_FILE=''
SC_MB_ADVISORIES_FILE=''

if not app.debug:
  logger = None

if app.debug:
  logging.config.fileConfig(LOGCONFFILE)
  logger = logging.getLogger('wq_rest_logger')
  logger.info("Log file opened")