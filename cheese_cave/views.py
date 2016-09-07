import os

from cheese_cave import app

from models import CheeseCave

if 'ENV' not in os.environ:
    exit("set the 'ENV' environment variable")

cheesecave = CheeseCave(os.environ.get('ENV'))

@app.route('/')
def home():
    latest_reading = cheesecave.get_latest_reading()
    current_target = cheesecave.get_current_target()
    return '\n<br>\n'.join([
        "Current Temp: {} degrees F".format(latest_reading['temp']),
        "Target Temp: {} degrees F (set {})".format(current_target['temp'],
                                                    current_target['date']),
        "Relative Humidity: {}%".format( latest_reading['humidity']),
        "",
        "Last updated {}".format(latest_reading['date']),
    ])


@app.route('/new_reading/<temp>/<humidity>')
def new_reading(temp, humidity):
    cheesecave.new_reading(temp, humidity)
    return home()

@app.route('/new_target/<temp>')
def new_target(temp):
    cheesecave.new_target(temp)
    return home()

@app.route('/get_target')
def get_target():
    return cheesecave.get_current_target()['temp']
