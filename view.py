from app import app
from flask import request
#import simplejson

def get_requested_station_data(station, start_date, end_date, station_directory):
  feature = None
  try:

    filepath = "%s/%s.json" % (station_directory, station)
    with open(filepath, "r") as jsonDataFile:
      jsonDataFile = open(filepath, "r")
      stationJson = geojson.load(jsonDataFile)

    resultList = []
    #If the client passed in a startdate parameter, we return only the test dates >= to it.
    if(startDate):
      startDate = datetime.datetime.strptime(startDate, "%Y-%m-%d")
      advisoryList = stationJson['properties']['test']['beachadvisories']
      for ndx in range(len(advisoryList)):
        tstDate = datetime.datetime.strptime(advisoryList[ndx]['date'], "%Y-%m-%d")
        if(tstDate >= startDate):
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
    if(logger):
      logger.exception(e)
  except ValueError, e:
    if(logger):
      logger.exception(e)
  except Exception, e:
    if(logger):
      logger.exception(e)
  try:
    if(feature is None):
      feature = geojson.Feature(id=station)

    jsonData = geojson.dumps(feature, separators=(',', ':'))



@app.route('/sarasota/current_results')
def get_sarasora_results():
  return 'You asked for Sarasota results.'


@app.route('/sarasota/predictions/current_results')
def get_sarasora_current_results():
  if logger:
    logger.debug("get_sarasora_current_results Started.")

  results = {'status': {'http_code': 404}}
  ret_code = 404
  try:
    with open(FL_SARASOTA_PREDICTIONS_FILE, 'r') as data_file:
      results = data_file.read()
      ret_code = 200
  except IOError,e:
    if logger:
      logger.exception(e)

  if logger:
    logger.debug("get_sarasora_current_results Finished.")

  return (results, ret_code, {'Content-Type': 'Application-JSON'})

@app.route('/sarasota/sample_data/current_results')
def get_sarasora_current_sample_data():
  if logger:
    logger.debug("get_sarasora_current_sample_data Started.")

  results = {'status': {'http_code': 404}}
  ret_code = 404
  try:
    with open(FL_SARASOTA_ADVISORIES_FILE, 'r') as data_file:
      results = data_file.read()
  except IOError,e:
    if logger:
      logger.exception(e)

  if logger:
    logger.debug("get_sarasora_current_sample_data Finished.")

  return (results, ret_code, {'Content-Type': 'Application-JSON'})

@app.route('/sarasota/station_data', methods=['GET'])
def get_sarasota_station_sample_data():
  ret_code = 404
  results = {}

  if logger:
    logger.debug("get_sarasota_station_sample_data Started")

  if logger:
    logger.debug("Request args: %s" % (request.args))

  if 'station' in request.args and 'startdate' in request.args:
    station = request.args['station']
    start_date = request.args['startdate']
    if logger:
      logger.debug("Station: %s Start Date: %s" % (station, start_date))

  if logger:
    logger.debug("get_sarasota_station_sample_data Finished")

  return (results, ret_code, {'Content-Type': 'Application-JSON'})

  return

