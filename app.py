#import sys
#sys.path.insert(0, '/Users/danramage/Documents/workspace/WaterQuality/wq_rest_interface')

from flask import Flask
import logging.config
from logging.handlers import RotatingFileHandler
from logging import Formatter
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from modules.pages_view import pages_view as pages_view_bp
from modules.rest_request_views import rest_requests as rest_requests_bp

from modules.admin_view import MyAdminIndexView, MyModelView, init_login
from models import User

#from flask_admin import Admin

app = Flask(__name__)

app.debug = True

app.register_blueprint(pages_view_bp)
app.register_blueprint(rest_requests_bp)

LOGFILE = '/var/log/wq_rest/flask_bp_site.log'


db = None
admin = None
def init_admin():
  init_login()
  admin = Admin(app, 'wq_app', index_view=MyAdminIndexView(), base_template='admin_master.html')
  # Create dummy secret key so we can use sessions
  app.config['SECRET_KEY'] = '123456790'

  # Create in-memory database
  app.config['DATABASE_FILE'] = 'sample_db.sqlite'
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
  app.config['SQLALCHEMY_ECHO'] = True
  db = SQLAlchemy(app)

  # Add view
  admin.add_view(MyModelView(User, db.session))


def init_logging():
  file_handler = RotatingFileHandler(filename = LOGFILE)
  file_handler.setLevel(logging.DEBUG)
  file_handler.setFormatter(Formatter('''
  Message type:       %(levelname)s
  Location:           %(pathname)s:%(lineno)d
  Module:             %(module)s
  Function:           %(funcName)s
  Time:               %(asctime)s

  Message:

  %(message)s
  '''))
  app.logger.addHandler(file_handler)
  #logging.config.fileConfig(LOGCONFFILE)
  #logger = logging.getLogger('wq_rest_logger')
  #logger.info("Log file opened")
  #app.logger = logging.getLogger('wq_rest_logger')
  return

if __name__ == '__main__':
  init_logging()
  init_admin()
  app.run(debug=True)
