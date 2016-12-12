import os
import sys
sys.path.insert(0, '/var/www/flaskdevhowsthebeach')

activate_this = os.path.join("/usr/local/virtualenv/python_flask/bin/activate_this.py")
execfile(activate_this, dict(__file__=activate_this))

from app import app as application
#from main import app as application