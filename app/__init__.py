import sys
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from config import *

app = Flask(__name__)

db = SQLAlchemy(app)

# Create in-memory database
app.config['DATABASE_FILE'] = DATABASE_FILE
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_ECHO'] = SQLALCHEMY_ECHO


"""
# Create user model.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(64))

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
      return self.username
"""

from admin_models import User
from wq_models import *


def install_secret_key(app, filename):
  """Configure the SECRET_KEY from a file
  in the instance directory.

  If the file does not exist, print instructions
  to create it from a shell with a random key,
  then exit.

  """
  """
  if not FLASK_DEBUG:
    filename = os.path.join(app.instance_path, filename)
    try:
        app.config['SECRET_KEY'] = open(filename, 'rb').read()
    except IOError:
        print 'Error: No secret key. Create it with:'
        if not os.path.isdir(os.path.dirname(filename)):
            print 'mkdir -p', os.path.dirname(filename)
        print 'head -c 24 /dev/urandom >', filename
        sys.exit(1)
  else:
    app.config['SECRET_KEY'] = SECRET_KEY
  """
  app.config['SECRET_KEY'] = SECRET_KEY
# Initialize flask-login
def init_login():
  login_manager = login.LoginManager()
  login_manager.init_app(app)

  # Create user loader function
  @login_manager.user_loader
  def load_user(user_id):
    return db.session.query(User).get(user_id)



def build_init_db(user, password):

  db.drop_all()
  db.create_all()
  # passwords are hashed, to use plaintext passwords instead:
  # test_user = User(login="test", password="test")
  test_user = User(login=user, password=generate_password_hash(password))
  db.session.add(test_user)
  db.session.commit()
  return


from view import *

init_login()
# Create admin
admin = admin.Admin(app, 'Water Quality Administation', index_view=MyAdminIndexView(), base_template='my_master.html')

# Add view
admin.add_view(MyModelView(User, db.session))
admin.add_view(wq_area_page(WQ_Area, db.session, name="Area"))
admin.add_view(wq_site_message_page(WQ_Site_Message, db.session, name="Area Message"))


#Page rules
app.add_url_rule('/', view_func=ShowIntroPage.as_view('intro_page'))
app.add_url_rule('/myrtlebeach', view_func=MyrtleBeachPage.as_view('myrtlebeach'))
app.add_url_rule('/sarasota', view_func=SarasotaPage.as_view('sarasota'))

#REST rules
app.add_url_rule('/predictions/current_results/<string:sitename>', view_func=PredictionsAPI.as_view('predictions_view'), methods=['GET'])
app.add_url_rule('/sample_data/current_results/<string:sitename>', view_func=BacteriaDataAPI.as_view('sample_data_view'), methods=['GET'])
app.add_url_rule('/station_data/<string:sitename>/<string:station_name>', view_func=StationDataAPI.as_view('station_data_view'), methods=['GET'])


@app.route('/<sitename>/rest/info')
def info_page(sitename):
  app.logger.debug("info_page for site: %s" % (sitename))

  if sitename == 'myrtlebeach':
    return send_from_directory('/var/www/flaskhowsthebeach/sites/myrtlebeach', 'info.html')
  elif sitename == 'sarasota':
    return send_from_directory('/var/www/flaskhowsthebeach/sites/sarasota', 'info.html')

@app.errorhandler(500)
def internal_error(exception):
    current_app.logger.exception(exception)
    #return render_template('500.html'), 500
"""
@app.route('/rest/help', methods = ['GET'])
def help():
  current_app.logger.debug("help started")
  func_list = {}
  for rule in app.url_map.iter_rules():
      if rule.endpoint != 'static':
          func_list[rule.rule] = app.view_functions[rule.endpoint].__doc__
  return jsonify(func_list)
"""