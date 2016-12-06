#import sys
#sys.path.insert(0, '/Users/danramage/Documents/workspace/WaterQuality/wq_rest_interface')

from main import logger
from flask import Flask, Blueprint, render_template

pages_view = Blueprint('pages_view', __name__,
                        template_folder='templates')

@pages_view.route('/')
def root():
  if logger:
    logger.debug("root Started.")
  return render_template("intro_page.html")


@pages_view.route('/<sitename>')
def index_page(sitename):
  if logger:
    logger.debug("index_page for site: %s" % (sitename))
  if sitename == "myrtlebeach":
    site_message = "ATTENTION: Due to Hurricane Matthew's damage of Springmaid Pier, data sources required for the forecasts are currently unavailable."
    return render_template('index_template.html', site_message=site_message)
  elif sitename == 'sarasota':
    site_message = None
    return render_template('index_template.html', site_message=site_message)
