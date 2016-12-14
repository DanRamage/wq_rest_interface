from flask import Flask
import logging.config
from view import *


app = Flask(__name__)
app.debug = True

LOGCONFFILE = '/var/www/flaskdevhowsthebeach/wq_rest.conf'
#LOGCONFFILE = '/Users/danramage/Documents/workspace/WaterQuality/wq_rest_interface/wq_rest_debug.conf'




if not app.debug:
  logger = None

if app.debug:
  logging.config.fileConfig(LOGCONFFILE)
  logger = logging.getLogger('wq_rest_logger')
  logger.info("Log file opened")

app.add_url_rule('/', view_func=ShowIntroPage.as_view('intro_page'))
app.add_url_rule('/myrtlebeach', view_func=MyrtleBeachPage.as_view('myrtlebeach'))
app.add_url_rule('/sarasota', view_func=MyrtleBeachPage.as_view('sarasota'))
