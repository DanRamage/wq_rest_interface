from flask import Flask
import logging.config
import simplejson


app = Flask(__name__)
app.debug = True

#LOGCONFFILE = '/var/www/wq_rest_interface/wq_rest.conf'
LOGCONFFILE = '/Users/danramage/Documents/workspace/WaterQuality/wq_rest_interface/wq_rest_debug.conf'



if not app.debug:
  logger = None

if app.debug:
  logging.config.fileConfig(LOGCONFFILE)
  logger = logging.getLogger('wq_rest_logger')
  logger.info("Log file opened")