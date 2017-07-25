import os
from flask import request, redirect, render_template, current_app, url_for, g
from flask.views import View, MethodView
from flask_admin import BaseView
from wtforms import form, fields, validators
import flask_admin as admin
import flask_login as login
from flask_admin.contrib import sqla
from flask_admin import helpers, expose
import time
import simplejson
import geojson
from datetime import datetime
from wtforms import form, fields, validators
from werkzeug.security import generate_password_hash, check_password_hash
from config import DEBUG_DATA_FILES
#from admin_models import User

from app import db
from admin_models import User
from wq_models import Project_Area, Site_Message, Project_Info_Page, Advisory_Limits

if not DEBUG_DATA_FILES:
  SC_RIVERS_PREDICTIONS_FILE='/home/xeniaprod/feeds/sc_rivers/Predictions.json'
  SC_RIVERS_ADVISORIES_FILE='/home/xeniaprod/feeds/sc_rivers/beachAdvisoryResults.json'
  SC_RIVERS_STATIONS_DATA_DIR='/home/xeniaprod/feeds/sc_rivers/monitorstations'
else:
  SC_RIVERS_PREDICTIONS_FILE='/home/xeniaprod/feeds/sc_rivers/debug/Predictions.json'
  SC_RIVERS_ADVISORIES_FILE='/home/xeniaprod/feeds/sc_rivers/debug/beachAdvisoryResults.json'
  SC_RIVERS_STATIONS_DATA_DIR='/home/xeniaprod/feeds/sc_rivers/debug/monitorstations'

class ShowIntroPage(View):
  def dispatch_request(self):
    current_app.logger.debug('intro_page rendered')
    return render_template("sc_rivers_intro.html")


class SitePage(View):
  def __init__(self, site_name):
    current_app.logger.debug('__init__')
    self.site_name = site_name

  def get_site_message(self):
    current_app.logger.debug('get_site_message started')
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
      rec = db.session.query(Project_Info_Page)\
        .join(Project_Area, Project_Area.id == Project_Info_Page.site_id)\
        .filter(Project_Area.area_name == self.site_name).first()
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
      sampling_program = ''
      url = ''
      description = ''
      swim_advisory_info = ''
      if rec is not None:
        if rec.sampling_program is not None:
          sampling_program = rec.sampling_program
        if rec.url is not None:
          url = rec.url
        if rec.description is not None:
          description = rec.description
        if rec.swim_advisory_info is not None:
          swim_advisory_info = rec.swim_advisory_info
      program_info = {
          'sampling_program': sampling_program,
          'url': url,
          'description': description,
          'advisory_limits': limits,
          'swim_advisory_info': swim_advisory_info
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
      if self.site_name == 'saluda':
        #Get prediction data
        prediction_data, ret_code = get_data_file(SC_RIVERS_PREDICTIONS_FILE)
        advisory_data, ret_code = get_data_file(SC_RIVERS_ADVISORIES_FILE)

      data = {
        'prediction_data': simplejson.loads(prediction_data),
        'advisory_data': simplejson.loads(advisory_data)
      }
    except Exception as e:
      current_app.logger.exception(e)
    current_app.logger.debug('get_data finished in %f seconds' % (time.time()-start_time))
    return data

  def dispatch_request(self):
    start_time = time.time()
    current_app.logger.debug('dispatch_request started')
    site_message = self.get_site_message()
    program_info = self.get_program_info()
    data = self.get_data()
    try:
      current_app.logger.debug('Site: %s rendered.' % (self.site_name))
      rendered_template = render_template('sc_rivers_index.html',
                             site_message=site_message,
                             site_name=self.site_name,
                             wq_site_bbox='',
                             sampling_program_info=program_info,
                             data=data)
    except Exception as e:
      current_app.logger.exception(e)
      rendered_template = render_template('sc_rivers_index.html',
                               site_message='',
                               site_name=self.site_name,
                               wq_site_bbox='',
                               sampling_program_info={},
                               data={})

    current_app.logger.debug('dispatch_request finished in %f seconds' % (time.time()-start_time))
    return rendered_template

class SaludaPage(SitePage):
  def __init__(self):
    current_app.logger.debug('SaludaPage __init__')
    SitePage.__init__(self, 'saluda')

def get_data_file(filename):
  current_app.logger.debug("get_data_file Started.")

  try:
    current_app.logger.debug("Opening file: %s" % (filename))
    with open(filename, 'r') as data_file:
      results = data_file.read()
      ret_code = 200

  except (Exception, IOError) as e:
    current_app.logger.exception(e)

    ret_code = 404
    results = simplejson.dumps({'status': {'http_code': ret_code},
                    'contents': None
                    })

  current_app.logger.debug("get_data_file Finished.")

  return results,ret_code

class SiteBaseAPI(MethodView):
  def __init__(self):
    self.site_name = None
    return


class PredictionsAPI(MethodView):
  def get(self, sitename=None):
    start_time = time.time()
    current_app.logger.debug('PredictionsAPI get for site: %s' % (sitename))
    ret_code = 404
    results = None

    if sitename == 'saluda':
      results, ret_code = get_data_file(SC_RIVERS_PREDICTIONS_FILE)
    else:
      results = simplejson.dumps({'status': {'http_code': ret_code},
                    'contents': None
                    })

    current_app.logger.debug('PredictionsAPI get for site: %s finished in %f seconds' % (sitename, time.time() - start_time))
    return (results, ret_code, {'Content-Type': 'Application-JSON'})


class BacteriaDataAPI(MethodView):
  def get(self, sitename=None):
    start_time = time.time()
    current_app.logger.debug('BacteriaDataAPI get for site: %s' % (sitename))
    ret_code = 404
    results = None

    if sitename == 'saluda':
      results, ret_code = get_data_file(SC_RIVERS_ADVISORIES_FILE)
      #Wrap the results in the status and contents keys. The app expects this format.
      json_ret = {'status': {'http_code': ret_code},
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

    current_app.logger.debug('StationDataAPI get for site: %s station: %s date: %s' % (sitename, station_name, start_date))
    ret_code = 404

    if sitename == 'saluda':
      results = self.get_requested_station_data(station_name, request, SC_RIVERS_STATIONS_DATA_DIR)
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
# Create customized model view class
class MyModelView(sqla.ModelView):

  def is_accessible(self):
    return login.current_user.is_authenticated


# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        current_app.logger.debug("Admin index page")
        if not login.current_user.is_authenticated:
          current_app.logger.debug("User: %s is not authenticated" % (login.current_user))
          return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        current_app.logger.debug("Login  page")
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

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
        current_app.logger.debug("Logout  page")
        login.logout_user()
        return redirect(url_for('.index'))


class base_view(sqla.ModelView):
  def create_model(self, form):
    try:
      model = self.model()
      form.populate_obj(model)
      model.user = login.current_user
      entry_time = datetime.utcnow()
      model.row_entry_date = entry_time.strftime("%Y-%m-%d %H:%M:%S")
      self.session.add(model)
      self._on_model_change(form, model, True)
      self.session.commit()
    except Exception as ex:
      current_app.logger.exception(ex)
      self.session.rollback()
      return False
    else:
      self.after_model_change(form, model, True)

    return model

  def update_model(self, form, model):
    try:
      update_time = datetime.utcnow()
      if model.row_entry_date is None:
        model.row_entry_date = update_time.strftime("%Y-%m-%d %H:%M:%S")
      model.row_update_date = update_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as ex:
      current_app.logger.exception(ex)
      self.session.rollback()
    return sqla.ModelView.update_model(self, form, model)


class project_type_view(base_view):
  column_list = ['name', 'row_entry_date', 'row_update_date']
  form_columns = ['name']
  def is_accessible(self):
    return login.current_user.is_authenticated

class project_area_view(base_view):
  column_list = ['area_name', 'display_name', 'row_entry_date', 'row_update_date']
  form_columns = ['area_name', 'display_name']

  def is_accessible(self):
    return login.current_user.is_authenticated


class site_message_view(base_view):
  column_list = ['site', 'message', 'row_entry_date', 'row_update_date']
  form_columns = ['site', 'message']
  def is_accessible(self):
    return login.current_user.is_authenticated

class site_message_level_view(base_view):
  column_list = ['message_level', 'row_entry_date', 'row_update_date']
  form_columns = ['message_level']
  def is_accessible(self):
    return login.current_user.is_authenticated

class project_info_view(base_view):
  def is_accessible(self):
    return login.current_user.is_authenticated

class advisory_limits_view(base_view):
  column_list = ['site', 'min_limit', 'max_limit', 'icon', 'limit_type', 'row_entry_date', 'row_update_date']
  form_columns = ['site_', 'min_limit', 'max_limit', 'icon', 'limit_type']
  def is_accessible(self):
    return login.current_user.is_authenticated
  """
  @expose('/')
  def index(self):
    if not login.current_user.is_authenticated:
        return redirect(url_for('.login_view'))
    return self.render('hello.html')
  """
