from flask import Flask, request
import logging.config
import simplejson

app = Flask(__name__)
app.debug = True

LOGCONFFILE = '/var/www/wq_rest_interface/wq_rest.conf'
#LOGCONFFILE = '/Users/danramage/Documents/workspace/WaterQuality/wq_rest_interface/wq_rest.conf'

FL_SARASOTA_PREDICTIONS_FILE='/mnt/fl_wq/Predictions.json'
FL_SARASOTA_ADVISORIES_FILE='/mnt/fl_wq/monitorstations/beachAdvisoryResults.json'

SC_MB_PREDICTIONS_FILE=''
SC_MB_ADVISORIES_FILE=''

if not app.debug:
  logger = None

if app.debug:
  logging.config.fileConfig(LOGCONFFILE)
  logger = logging.getLogger('wq_rest_logger')
  logger.info("Log file opened")

@app.route('/')
def hello_world():
  return 'Hello World!'

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
    logger.debug("%s" % (request.args))
  #station = request.form['station']
  #start_date = request.form['startdate']
  #if logger:
  #  logger.debug("Station: %s Start Date: %s" % (station, start_date))

  if logger:
    logger.debug("get_sarasota_station_sample_data Finished")

  return (results, ret_code, {'Content-Type': 'Application-JSON'})

  return

if __name__ == '__main__':
  app.run()
