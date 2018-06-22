FLASK_DEBUG = False
PYCHARM_DEBUG=False
# Create dummy secrey key so we can use sessions
SECRET_KEY = '123456790'
SECRET_KEY_FILE = 'secret_key'

# Create in-memory database
DATABASE_FILE = 'wq_db.sqlite'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_FILE
SQLALCHEMY_ECHO = False

IS_MAINTENANCE_MODE = False

if PYCHARM_DEBUG:
  LOGFILE='/Users/danramage/tmp/log/flask_plug_view_site.log'
else:
  LOGFILE='/var/log/wq_rest/flask_plug_view_site.log'

VALID_UPDATE_ADDRESSES = ['127.0.0.1', '129.252.139.113', '129.252.139.170']
CURRENT_SITE_LIST = ['myrtlebeach', 'sarasota', 'charleston', 'killdevilhill']

if not PYCHARM_DEBUG:
  SITES_CONFIG = {
    'myrtlebeach':
      {
        'prediction_file': '/mnt/sc_wq/vb_engine/Predictions.json',
        'advisory_file': '/mnt/sc_wq/vb_engine/monitorstations/beachAdvisoryResults.json',
        'stations_directory': '/mnt/sc_wq/vb_engine/monitorstations'
      },
    'sarasota':
      {
        'prediction_file': '/mnt/fl_wq/Predictions.json',
        'advisory_file': '/mnt/fl_wq/monitorstations/beachAdvisoryResults.json',
        'stations_directory': '/mnt/fl_wq/monitorstations'
      },
    'charleston':
      {
        'prediction_file': '/home/xeniaprod/feeds/charleston/Predictions.json',
        'advisory_file': '/home/xeniaprod/feeds/charleston/monitorstations/beach_advisories.json',
        'stations_directory': '/home/xeniaprod/feeds/charleston/monitorstations'
      },
      'killdevilhill':
      {
        'prediction_file': '/home/xeniaprod/feeds/northcarolina/killdevilhills/Predictions.json',
        'advisory_file': '/home/xeniaprod/feeds/northcarolina/killdevilhills/monitorstations/kdh_beach_advisories.json',
        'stations_directory': '/home/xeniaprod/feeds/northcarolina/killdevilhills/monitorstations'
      }
  }
else:
  SITES_CONFIG = {
    'myrtlebeach':
      {
        'prediction_file': '/Users/danramage/tmp/wq_feeds/sc_mb/Predictions.json',
        'advisory_file': '/Users/danramage/tmp/wq_feeds/sc_mb/monitorstations/beachAdvisoryResults.json',
        'stations_directory': '/Users/danramage/tmp/wq_feeds/sc_mb/monitorstations'
      },
    'charleston':
      {
        'prediction_file': '/Users/danramage/tmp/wq_feeds/charleston/Predictions.json',
        'advisory_file': '/Users/danramage/tmp/wq_feeds/charleston/monitorstations/beach_advisories.json',
        'stations_directory': '/Users/danramage/tmp/wq_feeds/charleston/monitorstations'
      },
      'killdevilhill':
      {
        'prediction_file': '/Users/danramage/tmp/wq_feeds/kdh/Predictions.json',
        'advisory_file': '/Users/danramage/tmp/wq_feeds/kdh/monitorstations/kdh_beach_advisories.json',
        'stations_directory': '/Users/danramage/tmp/wq_feeds/kdh/monitorstations'
      }
  }
