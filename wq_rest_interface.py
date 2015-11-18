from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
  return 'Hello World!'

@app.route('/sarasota/current_results')
def get_sarasora_results():
  return 'You asked for Sarasota results.'

@app.route('/myrtlebeach/current_results')
def get_mb_results():
  return 'You asked for Myrtle Beach results.'

if __name__ == '__main__':
  app.run()
