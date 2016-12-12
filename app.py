#import sys
#sys.path.insert(0, '/Users/danramage/Documents/workspace/WaterQuality/wq_rest_interface')

from main import logger
from flask import Flask
import logging.config

from modules.pages_view import pages_view as pages_view_bp
from modules.rest_request_views import rest_requests as rest_requests_bp

#from flask_admin import Admin

app = Flask(__name__)

app.register_blueprint(pages_view_bp)
app.register_blueprint(rest_requests_bp)

LOGCONFFILE = '/var/www/flaskdevhowsthebeach/wq_rest.conf'
#LOGCONFFILE = '/Users/danramage/Documents/workspace/WaterQuality/wq_rest_interface/wq_rest_debug.conf'

#admin = Admin(app, name='wqapp', template_mode='bootstrap3')



if app.debug:
  logging.config.fileConfig(LOGCONFFILE)
  logger = logging.getLogger('wq_rest_logger')
  logger.info("Log file opened")