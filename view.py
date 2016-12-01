import os
from app import app, logger
#from flask import request, send_from_directory, render_template
from flask import Flask
from datetime import datetime
import geojson
import simplejson

FL_SARASOTA_PREDICTIONS_FILE='/mnt/fl_wq/Predictions.json'
FL_SARASOTA_ADVISORIES_FILE='/mnt/fl_wq/monitorstations/beachAdvisoryResults.json'
FL_SARASOTA_STATIONS_DATA_DIR='/mnt/fl_wq/monitorstations'

SC_MB_PREDICTIONS_FILE='/mnt/sc_wq/Predictions.json'
SC_MB_ADVISORIES_FILE='/mnt/sc_wq/monitorstations/beachAdvisoryResults.json'
SC_MB_STATIONS_DATA_DIR='/mnt/sc_wq/monitorstations'

SC_DEV_MB_PREDICTIONS_FILE='/mnt/sc_wq/vb_engine/Predictions.json'
SC_DEV_MB_ADVISORIES_FILE='/mnt/sc_wq/vb_engine/monitorstations/beachAdvisoryResults.json'
SC_DEV_MB_STATIONS_DATA_DIR='/mnt/sc_wq/vb_engine/monitorstations'

#@app.route('/')
#def root():
#  if logger:
#    logger.debug("root Started.")
#  return send_from_directory('/var/www/howsthebeach/', 'index.html')



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

@app.route('/sarasota')
def sarasora_index_page():
  site_message = None
  return render_template('index_template.html', site_message=site_message)

@app.route('/myrtlebeach')
def myrtlebeach_index_page():
  site_message = "ATTENTION: Due to Hurricane Matthew's damage of Springmaid Pier, data sources required for the forecasts are currently unavailable."
  return render_template('index_template.html', site_message=site_message)


@app.route('/<string:sitename>/predictions/current_results')
def get_current_results(sitename):
  if logger:
    logger.debug("get_current_results for site: %s" % (sitename))
  if sitename == "myrtlebeach":
    return get_mb_current_results()
  elif sitename == 'sarasota':
    return get_sarasora_current_results()


@app.route('/<string:sitename>/sample_data/current_results')
def get_current_sample_data(sitename):
  if logger:
    logger.debug("get_current_sample_data for site: %s" % (sitename))
  if sitename == "myrtlebeach":
    return get_mb_current_sample_data()
  elif sitename == 'sarasota':
    return get_sarasora_current_sample_data()

@app.route('/<string:sitename>/station_data', methods=['GET'])
def get_station_sample_data(sitename):
  if logger:
    logger.debug("get_station_sample_data for site: %s" % (sitename))
  if sitename == "myrtlebeach":
    return get_mb_station_sample_data()
  elif sitename == 'sarasota':
    return get_sarasota_station_sample_data()


#@app.route('/myrtlebeach/predictions/current_results')
def get_mb_current_results():
  if logger:
    logger.debug("get_mb_current_results Started.")

  results, ret_code = get_data_file(SC_MB_PREDICTIONS_FILE)

  #Wrap the results in the status and contents keys. The app expects this format.
  json_ret = {'status' : {'http_code': ret_code},
              'contents': simplejson.loads(results)}
  results = simplejson.dumps(json_ret)

  if logger:
    logger.debug("get_mb_current_results Finished.")

  return (results, ret_code, {'Content-Type': 'Application-JSON'})

#@app.route('/myrtlebeach/sample_data/current_results')
def get_mb_current_sample_data():
  if logger:
    logger.debug("get_mb_current_sample_data Started.")

  results, ret_code = get_data_file(SC_MB_ADVISORIES_FILE)
  #Wrap the results in the status and contents keys. The app expects this format.
  json_ret = {'status' : {'http_code': ret_code},
              'contents': simplejson.loads(results)}
  results = simplejson.dumps(json_ret)

  if logger:
    logger.debug("get_mb_current_sample_data Finished.")

  return (results, ret_code, {'Content-Type': 'Application-JSON'})

#@app.route('/sarasota/predictions/current_results')
def get_sarasora_current_results():
  if logger:
    logger.debug("get_sarasora_current_results Started.")

  results, ret_code = get_data_file(FL_SARASOTA_PREDICTIONS_FILE)

  return (results, ret_code, {'Content-Type': 'Application-JSON'})

#@app.route('/sarasota/sample_data/current_results')
def get_sarasora_current_sample_data():
  if logger:
    logger.debug("get_sarasora_current_sample_data Started.")


  results,ret_code = get_data_file(FL_SARASOTA_ADVISORIES_FILE)
  #Wrap the results in the status and contents keys. The app expects this format.
  json_ret = {'status' : {'http_code': ret_code},
              'contents': simplejson.loads(results)}
  results = simplejson.dumps(json_ret)
  """
  results = {'status': {'http_code': 404}}
  try:
    with open(FL_SARASOTA_ADVISORIES_FILE, 'r') as data_file:
      results = data_file.read()
      ret_code = 200
  except IOError,e:
    if logger:
      logger.exception(e)
  """
  if logger:
    logger.debug("get_sarasora_current_sample_data Finished.")

  return (results, ret_code, {'Content-Type': 'Application-JSON'})

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

"""
@app.route('/myrtlebeach/info.html')
def mb_info_page():
  return send_from_directory('/var/www/howsthebeach/sites/myrtlebeach', 'info.html')

@app.route('/sarasota/info.html')
def sarasora_info_page():
  return send_from_directory('/var/www/howsthebeach/sites/sarasota', 'info.html')
"""

