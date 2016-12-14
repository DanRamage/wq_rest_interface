#import sys
#sys.path.insert(0, '/Users/danramage/Documents/workspace/WaterQuality/wq_rest_interface')
import os
from flask import Flask
import logging.config
from logging.handlers import RotatingFileHandler
from logging import Formatter
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
import flask_login as login

from modules.pages_view import pages_view as pages_view_bp
from modules.rest_request_views import rest_requests as rest_requests_bp

from modules.admin_view import MyAdminIndexView, MyModelView
from models import User, build_init_db

#from flask_admin import Admin

wq_app = Flask(__name__)

wq_app.debug = True

wq_app.register_blueprint(pages_view_bp)
wq_app.register_blueprint(rest_requests_bp)

#LOGFILE = '/var/log/wq_rest/flask_bp_site.log'
LOGFILE = '/Users/danramage/tmp/log/wq_rest.log'


db = None
admin = None

# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(wq_app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)

def init_admin():
  init_login()


  admin = Admin(wq_app, 'wq_app', index_view=MyAdminIndexView(), base_template='admin_master.html')
  # Create dummy secret key so we can use sessions
  wq_app.config['SECRET_KEY'] = '123456790'

  # Create in-memory database
  wq_app.config['DATABASE_FILE'] = 'sample_db.sqlite'
  wq_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + wq_app.config['DATABASE_FILE']
  wq_app.config['SQLALCHEMY_ECHO'] = True

  app_dir = os.path.realpath(os.path.dirname(__file__))
  database_path = os.path.join(app_dir, wq_app.config['DATABASE_FILE'])
  if not os.path.exists(database_path):
      build_init_db()

  db = SQLAlchemy(wq_app)

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
  wq_app.logger.addHandler(file_handler)
  #logging.config.fileConfig(LOGCONFFILE)
  #logger = logging.getLogger('wq_rest_logger')
  #logger.info("Log file opened")
  #wq_app.logger = logging.getLogger('wq_rest_logger')
  return

if __name__ == '__main__':
  init_logging()
  init_admin()
  wq_app.run(debug=True)
