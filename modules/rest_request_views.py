#import sys
#sys.path.insert(0, '/Users/danramage/Documents/workspace/WaterQuality/wq_rest_interface')

import os
from flask import Flask, request, Blueprint
from datetime import datetime
import geojson
import simplejson
import logging.config

FL_SARASOTA_PREDICTIONS_FILE='/mnt/fl_wq/Predictions.json'
FL_SARASOTA_ADVISORIES_FILE='/mnt/fl_wq/monitorstations/beachAdvisoryResults.json'
FL_SARASOTA_STATIONS_DATA_DIR='/mnt/fl_wq/monitorstations'

SC_MB_PREDICTIONS_FILE='/mnt/sc_wq/vb_engine/Predictions.json'
SC_MB_ADVISORIES_FILE='/mnt/sc_wq/monitorstations/beachAdvisoryResults.json'
SC_MB_STATIONS_DATA_DIR='/mnt/sc_wq/vb_engine/monitorstations'

#SC_MB_PREDICTIONS_FILE='/mnt/sc_wq/Predictions.json'
#SC_MB_ADVISORIES_FILE='/mnt/sc_wq/monitorstations/beachAdvisoryResults.json'
#SC_MB_STATIONS_DATA_DIR='/mnt/sc_wq/monitorstations'

SC_DEV_MB_PREDICTIONS_FILE='/mnt/sc_wq/vb_engine/Predictions.json'
SC_DEV_MB_ADVISORIES_FILE='/mnt/sc_wq/vb_engine/monitorstations/beachAdvisoryResults.json'
SC_DEV_MB_STATIONS_DATA_DIR='/mnt/sc_wq/vb_engine/monitorstations'

rest_requests = Blueprint('rest_requests', __name__,
                        template_folder='templates')

logger = logging.getLogger('wq_rest_logger')
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

@rest_requests.route('/<string:sitename>/rest/predictions/current_results')
def get_current_results(sitename):
  if logger:
    logger.debug("get_current_results for site: %s" % (sitename))
  if sitename == "myrtlebeach":
    return get_mb_current_results()
  elif sitename == 'sarasota':
    return get_sarasora_current_results()


@rest_requests.route('/<string:sitename>/rest/sample_data/current_results')
def get_current_sample_data(sitename):
  if logger:
    logger.debug("get_current_sample_data for site: %s" % (sitename))
  if sitename == "myrtlebeach":
    return get_mb_current_sample_data()
  elif sitename == 'sarasota':
    return get_sarasora_current_sample_data()

@rest_requests.route('/<string:sitename>/rest/station_data', methods=['GET'])
def get_station_sample_data(sitename):
  if logger:
    logger.debug("get_station_sample_data for site: %s" % (sitename))
  if sitename == "myrtlebeach":
    return get_mb_station_sample_data()
  elif sitename == 'sarasota':
    return get_sarasota_station_sample_data()

def get_mb_current_results():
  if logger:
    logger.debug("get_mb_current_results Started.")

  results, ret_code = get_data_file(SC_MB_PREDICTIONS_FILE)


  #Wrap the results in the status and contents keys. The app expects this format.
  #json_ret = {'status' : {'http_code': ret_code},
  #            'contents': simplejson.loads(results)}
  #results = simplejson.dumps(json_ret)

  if logger:
    logger.debug("get_mb_current_results Finished.")

  return (results, ret_code, {'Content-Type': 'Application-JSON'})

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

def get_sarasora_current_results():
  if logger:
    logger.debug("get_sarasora_current_results Started.")

  results, ret_code = get_data_file(FL_SARASOTA_PREDICTIONS_FILE)

  return (results, ret_code, {'Content-Type': 'Application-JSON'})

def get_sarasora_current_sample_data():
  if logger:
    logger.debug("get_sarasora_current_sample_data Started.")


  results,ret_code = get_data_file(FL_SARASOTA_ADVISORIES_FILE)
  #Wrap the results in the status and contents keys. The app expects this format.
  json_ret = {'status' : {'http_code': ret_code},
              'contents': simplejson.loads(results)}
  results = simplejson.dumps(json_ret)
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


