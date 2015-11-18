from flask import Flask
import logging.config
import simplejson

app = Flask(__name__)
app.debug = True

LOGCONFFILE = '/var/www/wq_rest_interface/wq_rest.conf'

FL_SARASOTA_PREDICTIONS_FILE='/mnt/fl_wq/Predictions.json'
FL_SARASOTA_ADVISORIES_FILE='/mnt/fl_wq/monitorstations/beachAdvisoryResults.json'

SC_MB_PREDICTIONS_FILE=''
SC_MB_ADVISORIES_FILE=''

logger = None
if app.debug:
  logger = logging.config.fileConfig(LOGCONFFILE)

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
  try:
    with open(FL_SARASOTA_PREDICTIONS_FILE, 'r') as fl_predictions_file:
      results = fl_predictions_file.read()
  except IOError,e:
    if logger:
      logger.exception(e)

  if logger:
    logger.debug("get_sarasora_current_results Finished.")

  return (results, 200, {'Content-Type': 'Application-JSON'})

if __name__ == '__main__':
  app.run()
