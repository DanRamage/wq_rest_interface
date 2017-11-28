import os
from flask import Flask, current_app, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import flask_admin as flask_admin
import flask_login as flask_login
from werkzeug.security import generate_password_hash,check_password_hash
from config import *
import logging.config
from logging.handlers import RotatingFileHandler
from logging import Formatter

#app = Flask(__name__)

#db = SQLAlchemy(app)
db = SQLAlchemy()
login_manager = flask_login.LoginManager()
"""
# Create in-memory database

app.config['DATABASE_FILE'] = DATABASE_FILE
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_ECHO'] = SQLALCHEMY_ECHO
"""

def create_app(config_file):
  app = Flask(__name__)

  install_secret_key(app)

  from app import db
  db.app = app
  db.init_app(app)

  # Create in-memory database
  app.config['DATABASE_FILE'] = DATABASE_FILE
  app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
  app.config['SQLALCHEMY_ECHO'] = SQLALCHEMY_ECHO

  init_logging(app)
  build_flask_admin(app)
  build_url_rules(app)

  return app

def build_flask_admin(app):

  from view import MyAdminIndexView, \
    AdminUserModelView, \
    BasicUserModelView, \
    RolesView,\
    project_area_view, \
    site_message_view, \
    project_type_view, \
    advisory_limits_view, \
    site_message_level_view, \
    sample_site_view, \
    boundary_view, \
    site_extent_view, \
    popup_site_view, \
    sample_site_data_view

  from admin_models import User, Role
  from wq_models import Project_Area, \
    Site_Message, \
    Project_Type, \
    Advisory_Limits, \
    Site_Message_Level, \
    Sample_Site, \
    Boundary, \
    Site_Extent, \
    Sample_Site_Data

  login_manager.init_app(app)
  # Create admin
  admin = flask_admin.Admin(app, 'Water Quality Administation', index_view=MyAdminIndexView(), base_template='my_master.html')

  # Add view
  admin.add_view(AdminUserModelView(User, db.session, endpoint="admin_user_view"))
  admin.add_view(BasicUserModelView(User, db.session, endpoint="basic_user_view"))
  admin.add_view(RolesView(Role, db.session))
  admin.add_view(project_type_view(Project_Type, db.session, name="Site Type"))
  admin.add_view(project_area_view(Project_Area, db.session, name="Area"))
  admin.add_view(site_message_view(Site_Message, db.session, name="Message"))
  admin.add_view(site_message_level_view(Site_Message_Level, db.session, name="Message Level"))
  admin.add_view(advisory_limits_view(Advisory_Limits, db.session, name="Advisory Limits"))
  admin.add_view(sample_site_view(Sample_Site, db.session, name="Sample Sites"))
  admin.add_view(boundary_view(Boundary, db.session, name="Boundaries"))
  admin.add_view(site_extent_view(Site_Extent, db.session, name="Site Extents"))
  admin.add_view(sample_site_data_view(Sample_Site_Data, db.session, name="Site Data"))

  admin.add_view(popup_site_view(Sample_Site, db.session, name="Popup Site", endpoint="popup_site_view"))

  return

def build_url_rules(app):
  from view import ShowIntroPage, \
    MyrtleBeachPage, \
    SarasotaPage, \
    CharlestonPage, \
    PredictionsAPI, \
    BacteriaDataAPI, \
    StationDataAPI, \
    MaintenanceMode

    #Page rules
  app.add_url_rule('/', view_func=ShowIntroPage.as_view('intro_page'))
  app.add_url_rule('/myrtlebeach', view_func=MyrtleBeachPage.as_view('myrtlebeach'))
  app.add_url_rule('/sarasota', view_func=SarasotaPage.as_view('sarasota'))
  app.add_url_rule('/charleston', view_func=CharlestonPage.as_view('charleston'))

  #REST rules
  app.add_url_rule('/predictions/current_results/<string:sitename>', view_func=PredictionsAPI.as_view('predictions_view'), methods=['GET'])
  app.add_url_rule('/sample_data/current_results/<string:sitename>', view_func=BacteriaDataAPI.as_view('sample_data_view'), methods=['GET'])
  app.add_url_rule('/station_data/<string:sitename>/<string:station_name>', view_func=StationDataAPI.as_view('station_data_view'), methods=['GET'])

  @app.before_request
  def check_for_maintenance():
    if IS_MAINTENANCE_MODE and request.path != url_for('maintenance'):
      return redirect(url_for('maintenance'))
      # Or alternatively, dont redirect
      # return 'Sorry, off for maintenance!', 503

  app.add_url_rule('/maintenance', view_func=MaintenanceMode.as_view('maintenance'))


  @app.errorhandler(500)
  def internal_error(exception):
      current_app.logger.exception(exception)
      #return render_template('500.html'), 500

  @app.errorhandler(404)
  def page_not_found(e):
    return render_template('404_page.html'), 404

  """
  @app.route('/<sitename>/rest/info')
  def info_page(sitename):
    app.logger.debug("info_page for site: %s" % (sitename))

    if sitename == 'myrtlebeach':
      return send_from_directory('/var/www/flaskhowsthebeach/sites/myrtlebeach', 'info.html')
    elif sitename == 'sarasota':
      return send_from_directory('/var/www/flaskhowsthebeach/sites/sarasota', 'info.html')
  """
  return

def init_logging(app):
  app.logger.setLevel(logging.DEBUG)
  file_handler = RotatingFileHandler(filename = LOGFILE)
  file_handler.setLevel(logging.DEBUG)
  file_handler.setFormatter(Formatter('%(asctime)s,%(levelname)s,%(module)s,%(funcName)s,%(lineno)d,%(message)s'))
  app.logger.addHandler(file_handler)

  app.logger.debug("Logging initialized")

  return

def install_secret_key(app):
  """Configure the SECRET_KEY from a file
  in the instance directory.

  If the file does not exist, print instructions
  to create it from a shell with a random key,
  then exit.

  """
  if not FLASK_DEBUG:
    app.config['SECRET_KEY'] = os.urandom(24)
  else:
    app.config['SECRET_KEY'] = SECRET_KEY


# Initialize flask-login
"""
def init_login(app):
  from admin_models import User

  login_manager.init_app(app)
"""
# Create user loader function
from admin_models import User
@login_manager.user_loader
def load_user(user_id):
  return db.session.query(User).get(user_id)


def create_user(user, password):
  test_user = User(login=user, password=generate_password_hash(password))
  db.session.add(test_user)
  db.session.commit()

def build_init_db(user, password):

  db.drop_all()
  db.create_all()
  # passwords are hashed, to use plaintext passwords instead:
  # test_user = User(login="test", password="test")
  test_user = User(login=user, password=generate_password_hash(password))
  db.session.add(test_user)
  db.session.commit()
  return

