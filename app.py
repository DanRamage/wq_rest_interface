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

#Page rules
app.add_url_rule('/', view_func=ShowIntroPage.as_view('intro_page'))
app.add_url_rule('/myrtlebeach', view_func=MyrtleBeachPage.as_view('myrtlebeach'))
app.add_url_rule('/sarasota', view_func=MyrtleBeachPage.as_view('sarasota'))

#REST rules
app.add_url_rule('/predictions/current_results/<string:sitename>', view_func=PredictionsAPI.as_view('predictions_view'), methods=['GET'])
app.add_url_rule('/sample_data/current_results/<string:sitename>', view_func=BacteriaDataAPI.as_view('sample_data_view'), methods=['GET'])
app.add_url_rule('/station_data/<string:sitename>/<string:station_name>', view_func=StationDataAPI.as_view('station_data_view'), methods=['GET'])

@app.route('/<sitename>/rest/info')
def info_page(sitename):
  if logger:
    logger.debug("info_page for site: %s" % (sitename))

  if sitename == 'myrtlebeach':
    return send_from_directory('/var/www/flaskhowsthebeach/sites/myrtlebeach', 'info.html')
  elif sitename == 'sarasota':
    return send_from_directory('/var/www/flaskhowsthebeach/sites/sarasota', 'info.html')

#@app.route('/myrtlebeach/info.html')
#def mb_info_page():
#  return send_from_directory('/var/www/howsthebeach/sites/myrtlebeach', 'info.html')

#@app.route('/sarasota/info.html')
#def sarasora_info_page():
#  return send_from_directory('/var/www/howsthebeach/sites/sarasota', 'info.html')

@app.route('/rest/help', methods = ['GET'])
def help():
  if logger:
    logger.debug("help started")
  """Print available functions."""
  func_list = {}
  for rule in app.url_map.iter_rules():
      if rule.endpoint != 'static':
          func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
  return jsonify(func_list)
