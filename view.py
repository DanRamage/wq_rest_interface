import os
from flask import Flask, request, send_from_directory, render_template, jsonify, current_app
from flask.views import View, MethodView

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

logger = None

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


class PredictionsAPI(MethodView):
  def get(self, sitename=None):
    current_app.logger.debug('PredictionsAPI get for site: %s' % (site))
    results = {}
    ret_code = 404
    if sitename == 'myrtlebeach':
      results, ret_code = self.get_data_file(SC_MB_PREDICTIONS_FILE)
    elif sitename == 'sarasota':
      results, ret_code = self.get_data_file(FL_SARASOTA_PREDICTIONS_FILE)

    return (results, ret_code, {'Content-Type': 'Application-JSON'})


  def get_data_file(self, filename):
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


class BacteriaDataAPI(MethodView):
  def get(self):
    return

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
