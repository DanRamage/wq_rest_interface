import os
from flask import Flask, request, send_from_directory, render_template, jsonify, current_app
from flask.views import View, MethodView
import simplejson
import geojson
from datetime import datetime

FL_SARASOTA_PREDICTIONS_FILE='/mnt/fl_wq/Predictions.json'
FL_SARASOTA_ADVISORIES_FILE='/mnt/fl_wq/monitorstations/beachAdvisoryResults.json'
FL_SARASOTA_STATIONS_DATA_DIR='/mnt/fl_wq/monitorstations'

SC_MB_PREDICTIONS_FILE='/mnt/sc_wq/vb_engine/Predictions.json'
SC_MB_ADVISORIES_FILE='/mnt/sc_wq/monitorstations/beachAdvisoryResults.json'
SC_MB_STATIONS_DATA_DIR='/mnt/sc_wq/monitorstations'

#SC_MB_PREDICTIONS_FILE='/mnt/sc_wq/Predictions.json'
#SC_MB_ADVISORIES_FILE='/mnt/sc_wq/monitorstations/beachAdvisoryResults.json'
#SC_MB_STATIONS_DATA_DIR='/mnt/sc_wq/monitorstations'

SC_DEV_MB_PREDICTIONS_FILE='/mnt/sc_wq/vb_engine/Predictions.json'
SC_DEV_MB_ADVISORIES_FILE='/mnt/sc_wq/vb_engine/monitorstations/beachAdvisoryResults.json'
SC_DEV_MB_STATIONS_DATA_DIR='/mnt/sc_wq/vb_engine/monitorstations'

class ShowIntroPage(View):
  def dispatch_request(self):
    current_app.logger.debug('intro_page rendered')
    return render_template("intro_page.html")

class SitePage(View):
  def __init__(self, site_name):
    current_app.logger.debug('SitePage __init__')
    self.site_name = site_name
    self.site_message = None

  def dispatch_request(self):
    current_app.logger.debug('Site: %s rendered' % (self.site_name))
    return render_template('index_template.html', site_message=self.site_message)


class MyrtleBeachPage(SitePage):
  def __init__(self):
    current_app.logger.debug('MyrtleBeachPage __init__')
    SitePage.__init__(self, 'myrtlebeach')
  def get_site_message(self):
    self.site_message = "ATTENTION: Due to Hurricane Matthew's damage of Springmaid Pier, data sources required for the forecasts are currently unavailable."

class SarasotaPage(SitePage):
  def __init__(self):
    current_app.logger.debug('SarasotaPage __init__')
    SitePage.__init__(self, 'sarasota')
  def get_site_message(self):
    self.site_message = None

def get_data_file(filename):
  current_app.logger.debug("get_data_file Started.")

  results = {'status': {'http_code': 404},
             'contents': {}}
  ret_code = 404

  try:
    current_app.logger.debug("Opening file: %s" % (filename))
    with open(filename, 'r') as data_file:
      #results['status']['http_code'] = 200
      #results['contents'] = simplejson.load(data_file)
      results = data_file.read()
      ret_code = 200

  except (Exception, IOError) as e:
    current_app.logger.exception(e)

  current_app.logger.debug("get_data_file Finished.")

  return results,ret_code

class PredictionsAPI(MethodView):
  def get(self, sitename=None):
    current_app.logger.debug('PredictionsAPI get for site: %s' % (sitename))
    results = {}
    ret_code = 404
    if sitename == 'myrtlebeach':
      results, ret_code = get_data_file(SC_MB_PREDICTIONS_FILE)
    elif sitename == 'sarasota':
      results, ret_code = get_data_file(FL_SARASOTA_PREDICTIONS_FILE)

    return (results, ret_code, {'Content-Type': 'Application-JSON'})


class BacteriaDataAPI(MethodView):
  def get(self, sitename=None):
    current_app.logger.debug('BacteriaDataAPI get for site: %s' % (sitename))
    results = {}
    ret_code = 404
    if sitename == 'myrtlebeach':
      results, ret_code = get_data_file(SC_MB_ADVISORIES_FILE)
      #Wrap the results in the status and contents keys. The app expects this format.
      json_ret = {'status': {'http_code': ret_code},
                  'contents': simplejson.loads(results)}
      results = simplejson.dumps(json_ret)

    elif sitename == 'sarasota':
      results,ret_code = get_data_file(FL_SARASOTA_ADVISORIES_FILE)
      #Wrap the results in the status and contents keys. The app expects this format.
      json_ret = {'status' : {'http_code': ret_code},
                  'contents': simplejson.loads(results)}
      results = simplejson.dumps(json_ret)

    return (results, ret_code, {'Content-Type': 'Application-JSON'})


class StationDataAPI(MethodView):
  def get(self, sitename=None, station_name=None):
    start_date = ''
    if 'startdate' in request.args:
      start_date = request.args['startdate']

    current_app.logger.debug('StationDataAPI get for site: %s station: %s date: %s' % (sitename, station_name, start_date))
    results = {}
    ret_code = 404

    if sitename == 'myrtlebeach':
      results = self.get_requested_station_data(request, SC_MB_STATIONS_DATA_DIR)
      ret_code = 200

    elif sitename == 'sarasota':
      results = self.get_requested_station_data(request, FL_SARASOTA_STATIONS_DATA_DIR)
      ret_code = 200

    return (results, ret_code, {'Content-Type': 'Application-JSON'})

  def get_requested_station_data(self, request, station_directory):

    current_app.logger.debug("get_requested_station_data Started")

    json_data = {'status': {'http_code': 404},
               'contents': {}}

    station = None
    start_date = None
    if 'station' in request.args:
      station = request.args['station']
    if 'startdate' in request.args:
      start_date = request.args['startdate']
    current_app.logger.debug("Station: %s Start Date: %s" % (station, start_date))

    feature = None
    try:
      filepath = os.path.join(station_directory, '%s.json' % (station))
      current_app.logger.debug("Opening station file: %s" % (filepath))

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
      current_app.logger.exception(e)
    except ValueError, e:
      current_app.logger.exception(e)
    except Exception, e:
      current_app.logger.exception(e)
    try:
      if feature is None:
        feature = geojson.Feature(id=station)

      json_data = {'status': {'http_code': 202},
                  'contents': feature
                  }
    except Exception, e:
      current_app.logger.exception(e)

    current_app.logger.debug("get_requested_station_data Finished")

    results = geojson.dumps(json_data, separators=(',', ':'))
    return results


"""
@app.route('/')
def root():
  if logger:
    logger.debug("root Started.")
  return render_template("intro_page.html")
"""

"""
@app.route('/<sitename>')
def index_page(sitename):
  if logger:
    logger.debug("index_page for site: %s" % (sitename))
  if sitename == "myrtlebeach":
    site_message = "ATTENTION: Due to Hurricane Matthew's damage of Springmaid Pier, data sources required for the forecasts are currently unavailable."
    return render_template('index_template.html', site_message=site_message)
  elif sitename == 'sarasota':
    site_message = None
    return render_template('index_template.html', site_message=site_message)
  return ""
"""
