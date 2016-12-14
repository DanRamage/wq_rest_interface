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
app.add_url_rule('/sample_data/current_results/<string:sitename>', view_func=BacteriaDataAPI.as_view('predictions_view'), methods=['GET'])

@app.route('/<sitename>/rest/info')
def info_page(sitename):
  if logger:
    logger.debug("info_page for site: %s" % (sitename))

  if sitename == 'myrtlebeach':
    return send_from_directory('/var/www/flaskhowsthebeach/sites/myrtlebeach', 'info.html')
  elif sitename == 'sarasota':
    return send_from_directory('/var/www/flaskhowsthebeach/sites/sarasota', 'info.html')

"""
@app.route('/myrtlebeach')
def myrtlebeach_index_page():
  site_message = "ATTENTION: Due to Hurricane Matthew's damage of Springmaid Pier, data sources required for the forecasts are currently unavailable."
  return render_template('index_template.html', site_message=site_message)
"""


def get_data_file(filename):
  if logger:
    logger.debug("get_data_file Started.")

  results = {'status': {'http_code': 404},
             'contents': {}}
  ret_code = 404

  try:
    with open(filename, 'r') as data_file:
      #results['status']['http_code'] = 200
      #results['contents'] = simplejson.load(data_file)
      results = data_file.read()
      ret_code = 200

  except (Exception, IOError) as e:
    if logger:
      logger.exception(e)

  if logger:
    logger.debug("get_data_file Finished.")

  return results,ret_code


@app.route('/<string:sitename>/rest/station_data', methods=['GET'])
def get_station_sample_data(sitename):
  if logger:
    logger.debug("get_station_sample_data for site: %s" % (sitename))
  if sitename == "myrtlebeach":
    return get_mb_station_sample_data()
  elif sitename == 'sarasota':
    return get_sarasota_station_sample_data()

def get_requested_station_data(request, station_directory):
  if logger:
    logger.debug("get_requested_station_data Started")

  json_data = {'status': {'http_code': 404},
             'contents': {}}

  station = None
  start_date = None
  if 'station' in request.args:
    station = request.args['station']
  if 'startdate' in request.args:
    start_date = request.args['startdate']
  if logger:
    logger.debug("Station: %s Start Date: %s" % (station, start_date))

  feature = None
  try:
    filepath = os.path.join(station_directory, '%s.json' % (station))
    if logger:
      logger.debug("Opening station file: %s" % (filepath))

    with open(filepath, "r") as json_data_file:
      stationJson = geojson.load(json_data_file)

    resultList = []
    #If the client passed in a startdate parameter, we return only the test dates >= to it.
    if start_date:
      start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
      advisoryList = stationJson['properties']['test']['beachadvisories']
      for ndx in range(len(advisoryList)):
        try:
          tst_date_obj = datetime.strptime(advisoryList[ndx]['date'], "%Y-%m-%d")
        except ValueError, e:
          tst_date_obj = datetime.strptime(advisoryList[ndx]['date'], "%Y-%m-%d %H:%M:%S")

        if tst_date_obj >= start_date_obj:
          resultList = advisoryList[ndx:]
          break
    else:
      resultList = stationJson['properties']['test']['beachadvisories'][-1]

    properties = {}
    properties['desc'] = stationJson['properties']['desc']
    properties['station'] = stationJson['properties']['station']
    properties['test'] = {'beachadvisories' : resultList}

    feature = geojson.Feature(id=station, geometry=stationJson['geometry'], properties=properties)
  except IOError, e:
    if logger:
      logger.exception(e)
  except ValueError, e:
    if logger:
      logger.exception(e)
  except Exception, e:
    if logger:
      logger.exception(e)
  try:
    if feature is None:
      feature = geojson.Feature(id=station)

    json_data = {'status': {'http_code': 202},
                'contents': feature
                }
  except Exception, e:
    if logger:
      logger.exception(e)

  if logger:
    logger.debug("get_requested_station_data Finished")

  results = geojson.dumps(json_data, separators=(',', ':'))
  return results

#@app.route('/sarasota/station_data', methods=['GET'])
def get_sarasota_station_sample_data():
  ret_code = 404
  results = {}

  if logger:
    logger.debug("get_sarasota_station_sample_data Started")

  if logger:
    logger.debug("Request args: %s" % (request.args))

    results = get_requested_station_data(request, FL_SARASOTA_STATIONS_DATA_DIR)
    ret_code = 200

  if logger:
    logger.debug("get_sarasota_station_sample_data Finished")

  return (results, ret_code, {'Content-Type': 'Application-JSON'})

#@app.route('/myrtlebeach/station_data', methods=['GET'])
def get_mb_station_sample_data():
  ret_code = 404
  results = {}

  if logger:
    logger.debug("get_mb_station_sample_data Started")

  if logger:
    logger.debug("Request args: %s" % (request.args))

    results = get_requested_station_data(request, SC_MB_STATIONS_DATA_DIR)
    ret_code = 200

  if logger:
    logger.debug("get_mb_station_sample_data Finished")

  return (results, ret_code, {'Content-Type': 'Application-JSON'})

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
