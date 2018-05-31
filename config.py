FLASK_DEBUG = False
PYCHARM_DEBUG=True
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
CURRENT_SITE_LIST = ['myrtlebeach', 'sarasota', 'charleston']