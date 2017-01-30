from app import create_app, build_init_db, init_logging
import optparse
from config import *


app = create_app(None)

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
    #install_secret_key(app, SECRET_KEY_FILE)
    init_logging(app)

    app.run(debug=True)
    app.logger.debug("App started")
