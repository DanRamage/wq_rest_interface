import os
from flask import request, redirect, render_template, current_app, url_for
from flask.views import View, MethodView
import flask_admin as admin
import flask_login as login
from flask_admin.contrib import sqla
from flask_admin import helpers, expose
from flask_security import Security, SQLAlchemyUserDatastore, \
    login_required, current_user
import time
import simplejson
import geojson
from datetime import datetime
from wtforms import form, fields, validators
from werkzeug.security import generate_password_hash, check_password_hash
from shapely.wkb import loads as wkb_loads
from shapely.wkt import loads as wkt_loads

from config import PYCHARM_DEBUG
from admin_models import User

from app import db
from admin_models import User
from wq_models import Project_Area, \
  Site_Message, \
  Advisory_Limits, \
  Sample_Site,\
  Site_Extent,\
  Boundary

if not PYCHARM_DEBUG:
  FL_SARASOTA_PREDICTIONS_FILE='/mnt/fl_wq/Predictions.json'
  FL_SARASOTA_ADVISORIES_FILE='/mnt/fl_wq/monitorstations/beachAdvisoryResults.json'
  FL_SARASOTA_STATIONS_DATA_DIR='/mnt/fl_wq/monitorstations'

  SC_MB_PREDICTIONS_FILE='/mnt/sc_wq/vb_engine/Predictions.json'
  SC_MB_ADVISORIES_FILE='/mnt/sc_wq/vb_engine/monitorstations/beachAdvisoryResults.json'
  SC_MB_STATIONS_DATA_DIR='/mnt/sc_wq/vb_engine/monitorstations'

  SC_CHS_PREDICTIONS_FILE='/home/xeniaprod/feeds/charleston/Predictions.json'
  SC_CHS_ADVISORIES_FILE='/home/xeniaprod/feeds/charleston/monitorstations/beach_advisories.json'
  SC_CHS_STATIONS_DATA_DIR='/home/xeniaprod/feeds/charleston/monitorstations'
else:
  SC_CHS_PREDICTIONS_FILE='/Users/danramage/tmp/Predictions.json'
  SC_CHS_ADVISORIES_FILE='/Users/danramage/tmp/beach_advisories.json'
  SC_CHS_STATIONS_DATA_DIR='/Users/danramage/tmp'

#SC_MB_PREDICTIONS_FILE='/mnt/sc_wq/Predictions.json'
#SC_MB_ADVISORIES_FILE='/mnt/sc_wq/monitorstations/beachAdvisoryResults.json'
#SC_MB_STATIONS_DATA_DIR='/mnt/sc_wq/monitorstations'

SC_DEV_MB_PREDICTIONS_FILE='/mnt/sc_wq/vb_engine/Predictions.json'
SC_DEV_MB_ADVISORIES_FILE='/mnt/sc_wq/vb_engine/monitorstations/beachAdvisoryResults.json'
SC_DEV_MB_STATIONS_DATA_DIR='/mnt/sc_wq/vb_engine/monitorstations'

def build_feature(sample_site_rec, sample_date, values):
  beachadvisories = {
    'date': '',
    'station': sample_site_rec.site_name,
    'value': ''
  }
  if len(values):
    beachadvisories = {
      'date': sample_date,
      'station': sample_site_rec.site_name,
      'value': values
    }
  feature = {
    'type': 'Feature',
    'geometry': {
      'type': 'Point',
      'coordinates': [sample_site_rec.longitude, sample_site_rec.latitude]
    },
    'properties': {
      'locale': sample_site_rec.description,
      'sign': False,
      'station': sample_site_rec.site_name,
      'epaid': sample_site_rec.epa_id,
      'beach': sample_site_rec.county,
      'desc': sample_site_rec.description,
      'has_advisory': sample_site_rec.has_current_advisory,
      'station_message': sample_site_rec.advisory_text,
      'len': '',
      'test': {
        'beachadvisories': beachadvisories
      }
    }
  }
  extents_json = None
  if len(sample_site_rec.extents):
    extents_json = geojson.Feature(geometry=sample_site_rec.extents[0].wkt_extent, properties={})
    feature['properties']['extents_geometry'] = extents_json

  return feature

class MaintenanceMode(View):
  def dispatch_request(self):
    current_app.logger.debug('IP: %s MaintenanceMode rendered' % (request.remote_addr))
    return render_template("MaintenanceMode.html")

class ShowIntroPage(View):
  def dispatch_request(self):
    current_app.logger.debug('IP: %s intro_page rendered' % (request.remote_addr))
    return render_template("intro_page.html")

class SitePage(View):
  def __init__(self, site_name):
    current_app.logger.debug('__init__')
    self.site_name = site_name
    self.page_template = 'index_template.html'

  def get_site_message(self):
    current_app.logger.debug('IP: %s get_site_message started' % (request.remote_addr))
    start_time = time.time()
    rec = db.session.query(Site_Message)\
      .join(Project_Area, Project_Area.id == Site_Message.site_id)\
      .filter(Project_Area.area_name == self.site_name).first()
    current_app.logger.debug('get_site_message finished in %f seconds' % (time.time()-start_time))
    return rec

  def get_program_info(self):
    current_app.logger.debug('get_program_info started')
    start_time = time.time()
    program_info = {}
    try:
      """
      rec = db.session.query(Project_Info_Page)\
        .join(Project_Area, Project_Area.id == Project_Info_Page.site_id)\
        .filter(Project_Area.area_name == self.site_name).first()
      """
      #Get the advisroy limits
      limit_recs = db.session.query(Advisory_Limits)\
        .join(Project_Area, Project_Area.id == Advisory_Limits.site_id)\
        .filter(Project_Area.area_name == self.site_name)\
        .order_by(Advisory_Limits.min_limit).all()
      limits = {}
      for limit in limit_recs:
        limits[limit.limit_type] = {
          'min_limit': limit.min_limit,
          'max_limit': limit.max_limit,
          'icon': limit.icon
        }
      program_info = {
          #'sampling_program': rec.sampling_program,
          #'url': rec.url,
          #'description': rec.description,
          'advisory_limits': limits,
          #'swim_advisory_info': rec.swim_advisory_info
        }
    except Exception as e:
      current_app.logger.exception(e)
    current_app.logger.debug('get_program_info finished in %f seconds' % (time.time()-start_time))
    return program_info

  def get_data(self):
    current_app.logger.debug('get_data started')
    start_time = time.time()
    data = {}
    try:
      if self.site_name == 'myrtlebeach':
        #Get prediction data
        prediction_data, ret_code = get_data_file(SC_MB_PREDICTIONS_FILE)
        advisory_data, ret_code = get_data_file(SC_MB_ADVISORIES_FILE)
      elif self.site_name == 'sarasota':
        prediction_data, ret_code = get_data_file(FL_SARASOTA_PREDICTIONS_FILE)
        advisory_data,ret_code = get_data_file(FL_SARASOTA_ADVISORIES_FILE)
      elif self.site_name == 'charleston':
        prediction_data, ret_code = get_data_file(SC_CHS_PREDICTIONS_FILE)
        advisory_data,ret_code = get_data_file(SC_CHS_ADVISORIES_FILE)

      data = {
        'prediction_data': simplejson.loads(prediction_data),
        'advisory_data': simplejson.loads(advisory_data)
      }
      #Query the database to see if we have any temporary popup sites.
      popup_sites = db.session.query(Sample_Site) \
        .join(Project_Area, Project_Area.id == Sample_Site.project_site_id) \
        .filter(Project_Area.area_name == self.site_name)\
        .filter(Sample_Site.temporary_site == True).all()
      if len(popup_sites):
        advisory_data_features = data['advisory_data']['features']
        for site in popup_sites:
          sample_date = site.row_entry_date
          sample_value = []
          if len(site.site_data):
            sample_date = site.site_data[0].sample_date
            sample_value.append(site.site_data[0].sample_value)
          feature = build_feature(site, sample_date, sample_value)
          advisory_data_features.append(feature)
    except Exception as e:
      current_app.logger.exception(e)
    current_app.logger.debug('get_data finished in %f seconds' % (time.time()-start_time))
    return data

  def dispatch_request(self):
    start_time = time.time()
    current_app.logger.debug('IP: %s dispatch_request started' % (request.remote_addr))
    site_message = self.get_site_message()
    program_info = self.get_program_info()
    data = self.get_data()
    try:
      current_app.logger.debug('Site: %s rendered.' % (self.site_name))
      rendered_template = render_template(self.page_template,
                             site_message=site_message,
                             site_name=self.site_name,
                             wq_site_bbox='',
                             sampling_program_info=program_info,
                             data=data)
    except Exception as e:
      current_app.logger.exception(e)
      rendered_template = render_template(self.page_template,
                               site_message='',
                               site_name=self.site_name,
                               wq_site_bbox='',
                               sampling_program_info={},
                               data={})

    current_app.logger.debug('dispatch_request finished in %f seconds' % (time.time()-start_time))
    return rendered_template

class MyrtleBeachPage(SitePage):
  def __init__(self):
    current_app.logger.debug('IP: %s MyrtleBeachPage __init__' % (request.remote_addr))
    SitePage.__init__(self, 'myrtlebeach')
    self.page_template = 'mb_index_page.html'


class SarasotaPage(SitePage):
  def __init__(self):
    current_app.logger.debug('IP: %s SarasotaPage __init__' % (request.remote_addr))
    SitePage.__init__(self, 'sarasota')
    self.page_template = 'sarasota_index_page.html'

class CharlestonPage(SitePage):
  def __init__(self):
    current_app.logger.debug('IP: %s CharlestonPage __init__' % (request.remote_addr))
    SitePage.__init__(self, 'charleston')
    self.page_template = 'chs_index_page.html'

def get_data_file(filename):
  current_app.logger.debug("get_data_file Started.")

  ret_code = 404
  results = {'status': {'http_code': ret_code},
                'contents': None
                }

  try:
    current_app.logger.debug("Opening file: %s" % (filename))
    with open(filename, 'r') as data_file:
      results = data_file.read()
      ret_code = 200

  except (Exception, IOError) as e:
    current_app.logger.exception(e)

  current_app.logger.debug("get_data_file Finished.")

  return results,ret_code

class SiteBaseAPI(MethodView):
  def __init__(self):
    self.site_name = None
    return


class PredictionsAPI(MethodView):
  def get(self, sitename=None):
    start_time = time.time()
    current_app.logger.debug('IP: %s PredictionsAPI get for site: %s' % (request.remote_addr, sitename))
    ret_code = 404
    results = None

    if sitename == 'myrtlebeach':
      results, ret_code = get_data_file(SC_MB_PREDICTIONS_FILE)
    elif sitename == 'sarasota':
      results, ret_code = get_data_file(FL_SARASOTA_PREDICTIONS_FILE)
    elif sitename == 'charleston':
      results, ret_code = get_data_file(SC_CHS_PREDICTIONS_FILE)

    else:
      results = simplejson.dumps({'status': {'http_code': ret_code},
                    'contents': None
                    })

    current_app.logger.debug('PredictionsAPI get for site: %s finished in %f seconds' % (sitename, time.time() - start_time))
    return (results, ret_code, {'Content-Type': 'Application-JSON'})


class BacteriaDataAPI(MethodView):
  def get(self, sitename=None):
    start_time = time.time()
    current_app.logger.debug('IP: %s BacteriaDataAPI get for site: %s' % (request.remote_addr, sitename))
    ret_code = 404
    results = None

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

    elif sitename == 'charleston':
      results,ret_code = get_data_file(SC_CHS_ADVISORIES_FILE)
      #Wrap the results in the status and contents keys. The app expects this format.
      json_ret = {'status' : {'http_code': ret_code},
                  'contents': simplejson.loads(results)}
      results = simplejson.dumps(json_ret)

    else:
      results = simplejson.dumps({'status': {'http_code': ret_code},
                    'contents': None
                    })

    current_app.logger.debug('BacteriaDataAPI get for site: %s finished in %f seconds' % (sitename, time.time() - start_time))
    return (results, ret_code, {'Content-Type': 'Application-JSON'})


class StationDataAPI(MethodView):
  def get(self, sitename=None, station_name=None):
    start_date = ''
    if 'startdate' in request.args:
      start_date = request.args['startdate']

    current_app.logger.debug('IP: %s StationDataAPI get for site: %s station: %s date: %s' % (request.remote_addr, sitename, station_name, start_date))
    ret_code = 404

    if sitename == 'myrtlebeach':
      results = self.get_requested_station_data(station_name, request, SC_MB_STATIONS_DATA_DIR)
      ret_code = 200

    elif sitename == 'sarasota':
      results = self.get_requested_station_data(station_name, request, FL_SARASOTA_STATIONS_DATA_DIR)
      ret_code = 200

    elif sitename == 'charleston':
      results = self.get_requested_station_data(station_name, request, SC_CHS_STATIONS_DATA_DIR)
      ret_code = 200

    else:
      results = simplejson.dumps({'status': {'http_code': ret_code},
                    'contents': None
                    })

    return (results, ret_code, {'Content-Type': 'Application-JSON'})

  def get_requested_station_data(self, station, request, station_directory):
    start_time = time.time()
    ret_code = 404
    current_app.logger.debug("get_requested_station_data Started")

    json_data = {'status': {'http_code': 404},
               'contents': {}}

    start_date = None
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
      ret_code = 200

    except (IOError, ValueError, Exception) as e:
      current_app.logger.exception(e)
    try:
      if feature is None:
        feature = geojson.Feature(id=station)

      json_data = {'status': {'http_code': ret_code},
                  'contents': feature
                  }
    except Exception, e:
      current_app.logger.exception(e)


    results = geojson.dumps(json_data, separators=(',', ':'))
    current_app.logger.debug("get_requested_station_data finished in %s seconds" % (time.time() - start_time))
    return results


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
      user = self.get_user()

      if user is None:
          raise validators.ValidationError('Invalid user')

      # we're comparing the plaintext pw with the the hash from the db
      if not check_password_hash(user.password, self.password.data):
      # to compare plain text passwords use
      # if user.password != self.password.data:
          raise validators.ValidationError('Invalid password')

    def get_user(self):
      return db.session.query(User).filter_by(login=self.login.data).first()


"""
class RegistrationForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    email = fields.StringField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
      if db.session.query(User).filter_by(login=self.login.data).count() > 0:
        raise validators.ValidationError('Duplicate username')
"""

class base_view(sqla.ModelView):
  """
  This view is used to update some common columns across all the tables used.
  Now it's mostly the row_entry_date and row_update_date.
  """
  def on_model_change(self, form, model, is_created):
    start_time = time.time()
    current_app.logger.debug("IP: %s User: %s on_model_change started" % (request.remote_addr, current_user.login))

    entry_time = datetime.utcnow()
    if is_created:
      model.row_entry_date = entry_time.strftime("%Y-%m-%d %H:%M:%S")
    else:
      model.row_update_date = entry_time.strftime("%Y-%m-%d %H:%M:%S")

    sqla.ModelView.on_model_change(self, form, model, is_created)

    current_app.logger.debug("IP: %s User: %s on_model_change finished in %f seconds" % (request.remote_addr, current_user.login, time.time() - start_time))

  def is_accessible(self):
    """
    This checks to make sure the user is active and authenticated and is a superuser. Otherwise
    the view is not accessible.
    :return:
    """
    if not current_user.is_active or not current_user.is_authenticated:
      return False

    if current_user.has_role('superuser'):
      return True

    return False

class AdminUserModelView(base_view):
  """
  This view handles the administrative user editing/creation of users.
  """
  form_extra_fields = {
    'password': fields.PasswordField('Password')
  }
  column_list = ('login', 'first_name', 'last_name', 'email', 'active', 'roles', 'row_entry_date', 'row_update_date')
  form_columns = ('login', 'first_name', 'last_name', 'email', 'password', 'active', 'roles')

  def on_model_change(self, form, model, is_created):
    """
    If we're creating a new user, hash the password entered, if we're updating, check if password
    has changed and then hash that.
    :param form:
    :param model:
    :param is_created:
    :return:
    """
    start_time = time.time()
    current_app.logger.debug(
      'IP: %s User: %s AdminUserModelView on_model_change started.' % (request.remote_addr, current_user.login))
    # Hash the password text if we're creating a new user.
    if is_created:
      model.password = generate_password_hash(form.password.data)
    # If this is an update, check to see if password has changed and if so hash the form password.
    else:
      hashed_pwd = generate_password_hash(form.password.data)
      if hashed_pwd != model.password:
        model.password = hashed_pwd

    current_app.logger.debug('IP: %s User: %s AdminUserModelView create_model finished in %f seconds.' % (
    request.remote_addr, current_user.login, time.time() - start_time))

class BasicUserModelView(AdminUserModelView):
  """
  Basic user view. A simple user only gets access to their data record to edit. No creating or deleting.
  """
  column_list = ('login', 'first_name', 'last_name', 'email')
  form_columns = ('login', 'first_name', 'last_name', 'email', 'password')
  can_create = False  # Don't allow a basic user ability to add a new user.
  can_delete = False  # Don't allow user to delete records.

  def get_query(self):
    # Only return the record that matches the logged in user.
    return super(AdminUserModelView, self).get_query().filter(User.login == login.current_user.login)

  def is_accessible(self):
    if current_user.is_active and current_user.is_authenticated and not current_user.has_role('superuser'):
      return True
    return False

class RolesView(base_view):
  """
  View into the user Roles table.
  """
  column_list = ['name', 'description']
  form_columns = ['name', 'description']


# Create customized model view class
class MyModelView(sqla.ModelView):

  def is_accessible(self):
    return login.current_user.is_authenticated



# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        current_app.logger.debug("IP: %s Admin index page" % (request.remote_addr))
        if not login.current_user.is_authenticated:
          current_app.logger.debug("User: %s is not authenticated" % (login.current_user))
          return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        current_app.logger.debug("IP: %s Login page" % (request.remote_addr))
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)
        else:
          current_app.logger.debug("IP: %s User: %s is not authenticated" % (request.remote_addr, form.login.data))
        if login.current_user.is_authenticated:
            return redirect(url_for('.index'))
        #link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        #self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()
    """
    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()

            form.populate_obj(user)
            # we hash the users password to avoid saving it as plaintext in the db,
            # remove to use plain text:
            user.password = generate_password_hash(form.password.data)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))

        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()
    """
    @expose('/logout/')
    def logout_view(self):
        current_app.logger.debug("IP: %s Logout page" % (request.remote_addr))
        login.logout_user()
        return redirect(url_for('.index'))


class project_type_view(base_view):
  column_list = ['name', 'row_entry_date', 'row_update_date']
  form_columns = ['name']

class project_area_view(base_view):
  column_list = ['area_name', 'display_name', 'row_entry_date', 'row_update_date']
  form_columns = ['area_name', 'display_name']

class site_message_view(base_view):
  column_list = ['site', 'message', 'row_entry_date', 'row_update_date']
  form_columns = ['site', 'message']

  def is_accessible(self):
    if current_user.is_active and current_user.is_authenticated:
      return True
    return False

class site_message_level_view(base_view):
  column_list = ['message_level', 'row_entry_date', 'row_update_date']
  form_columns = ['message_level']

class advisory_limits_view(base_view):
  column_list = ['site', 'min_limit', 'max_limit', 'icon', 'limit_type', 'row_entry_date', 'row_update_date']
  form_columns = ['site', 'min_limit', 'max_limit', 'icon', 'limit_type']

class sample_site_view(base_view):
  """
  View for the Sample_Site table.
  """
  column_list = ['project_site', 'site_name', 'latitude', 'longitude', 'description', 'epa_id', 'county', 'issues_advisories', 'has_current_advisory', 'advisory_text', 'boundaries', 'temporary_site', 'site_data', 'row_entry_date', 'row_update_date']
  form_columns = ['project_site', 'site_name', 'latitude', 'longitude', 'description', 'epa_id', 'county', 'site_data','issues_advisories', 'has_current_advisory', 'advisory_text', 'boundaries', 'temporary_site']
  column_filters = ['project_site']

  def on_model_change(self, form, model, is_created):
    """
    When a new record is created or editing, we want to take the values in the lat/long field
    and populate the wkt_location field.
    :param form:
    :param model:
    :param is_created:
    :return:
    """
    start_time = time.time()
    current_app.logger.debug('IP: %s User: %s popup_site_view on_model_change started.' % (request.remote_addr, current_user.login))

    if is_created:
      entry_time = datetime.utcnow()
      model.row_entry_date = entry_time.strftime("%Y-%m-%d %H:%M:%S")

    model.user = login.current_user
    """
    if len(model.wkt_location) and form.longitude.data is None and form.latitude.data is None:
      points = model.wkt_location.replace('POINT(', '').replace(')', '')
      longitude,latitude = points.split(' ')
      form.longitude.data = float(longitude)
      form.latitude.data = float(latitude)
    else:
      wkt_location = "POINT(%s %s)" % (form.longitude.data, form.latitude.data)
      model.wkt_location = wkt_location
    """
    base_view.on_model_change(self, form, model, is_created)

    current_app.logger.debug('IP: %s User: %s popup_site_view on_model_change finished in %f seconds.' % (request.remote_addr, current_user.login, time.time() - start_time))

class wktTextField(fields.TextAreaField):
  def process_data(self, value):
    self.data = wkb_loads(value)

class boundary_view(base_view):
  #Instead of showing the binary of the wkb_boundary field, we convert to the wkt
  #and diplay it.
  #Formatter to convert the wkb to wkt for display.
  def _wkb_to_wkt(view, context, model, name):
    wkt = wkb_loads(model.wkb_boundary)
    return wkt

  form_extra_fields = {
    'wkb_boundary': wktTextField('Boundary Polygon')
  }
  column_formatters = {
    'wkb_boundary': _wkb_to_wkt
  }
  column_list = ['project_site', 'boundary_name', 'wkb_boundary', 'row_entry_date', 'row_update_date']
  form_columns = ['project_site', 'boundary_name', 'wkb_boundary']
  column_filters = ['project_site']

  def on_model_change(self, form, model, is_created):
    """
    Handle the wkt to wkb to store in the database.
    :param form:
    :param model:
    :param is_created:
    :return:
    """
    start_time = time.time()
    current_app.logger.debug(
      'IP: %s User: %s boundary_view on_model_change started.' % (request.remote_addr, current_user.login))
    geom = wkt_loads(form.wkb_boundary.data)
    model.wkb_boundary = geom.wkb

    base_view.on_model_change(self, form, model, is_created)

    current_app.logger.debug('IP: %s User: %s boundary_view create_model finished in %f seconds.' % (
    request.remote_addr, current_user.login, time.time() - start_time))


class site_extent_view(base_view):
  column_list = ['sample_site', 'extent_name', 'wkt_extent', 'row_entry_date', 'row_update_date']
  form_columns = ['sample_site', 'extent_name', 'wkt_extent']

class popup_site_view(base_view):

  column_list = ['project_site', 'site_name', 'latitude', 'longitude', 'description', 'advisory_text']
  form_columns = ['project_site', 'site_name', 'latitude', 'longitude', 'description', 'advisory_text']
  column_filters = ['project_site']

  def on_model_change(self, form, model, is_created):
    start_time = time.time()
    current_app.logger.debug('IP: %s User: %s popup_site_view on_model_change started.' % (request.remote_addr, current_user.login))

    model.temporary_site = True
    model.wkt_location = "POINT(%s %s)" % (form.longitude.data, form.latitude.data)
    base_view.on_model_change(self, form, model, is_created)

    current_app.logger.debug('IP: %s User: %s popup_site_view on_model_change finished in %f seconds.' % (request.remote_addr, current_user.login, time.time() - start_time))

  def get_query(self):
    #For this view we only return the sites that are temporary, not the main sampleing sites.
    return super(popup_site_view, self).get_query().filter(Sample_Site.temporary_site == True)

  def is_accessible(self):
    if current_user.is_active and current_user.is_authenticated:
      return True
    return False

class sample_site_data_view(base_view):
  column_list=['sample_site_name', 'sample_date', 'sample_value', 'row_entry_date', 'row_update_date']
  form_columns=['sample_site_name', 'sample_date', 'sample_value']
  column_filters = ['sample_site_name']

