from flask import Flask
from app import app, build_init_db, install_secret_key
import optparse
from config import *




"""
def create_app(config_file):
  app = Flask(__name__)

  from app import db
  db.app = app
  db.init_app(app)

  # Create in-memory database
  app.config['DATABASE_FILE'] = DATABASE_FILE
  app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
  app.config['SQLALCHEMY_ECHO'] = SQLALCHEMY_ECHO

"""



if __name__ == '__main__':
  parser = optparse.OptionParser()

  parser.add_option("-u", "--User", dest="user",
                    help="User to add", default=None)
  parser.add_option("-p", "--Password", dest="password",
                    help="Stations file to import.", default=None )
  (options, args) = parser.parse_args()


  if(options.user is not None):
    if(options.password is not None):
      build_init_db(options.user, options.password)
    else:
      print("Must provide password")
  else:
    install_secret_key(app, SECRET_KEY_FILE)
    app.run(debug=FLASK_DEBUG)
    app.logger.debug("App started")
