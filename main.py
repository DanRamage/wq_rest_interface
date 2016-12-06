logger = None

from app import app
#from view import *

app.debug = True
if not app.debug:
  logger = None

if __name__ == '__main__':
  app.run()
