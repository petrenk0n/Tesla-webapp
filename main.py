import smartcar
from flask import Flask, redirect, request, jsonify, render_template
from flask_cors import CORS

import os

app = Flask(__name__)
CORS(app)

# global variable to save our access_token
access = None

# Client object
client = smartcar.AuthClient(
  client_id='CLIENT_ID',
  client_secret='CLIENT_SECRET',
  redirect_uri='REDIRECT_URI',
  scope=['read_odometer', 'read_vehicle_info', 'read_battery', 'required:read_location', 'read_tires', 'control_security'],
  test_mode = True
)

auth_url = client.get_auth_url(state='0facda3319')

# Authenticate with the car manufacturer
@app.route('/login', methods=['GET'])
def login():
    auth_url = client.get_auth_url()
    return redirect(auth_url)

# Receive vehicle exchange code
@app.route('/exchange', methods=['GET'])
def exchange():
    code = request.args.get('code')
    # access our global variable and store our access tokens
    global access
    # in a production app you'll want to store this in some kind of
    # persistent storage
    access = client.exchange_code(code)
    return redirect('/vehicle')

# Main control panel
@app.route('/vehicle', methods=['GET'])
def vehicle():
    # access our global variable to retrieve our access tokens
    global access
    # the list of vehicle ids
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']

    # instantiate the first vehicle in the vehicle id list
    vehicle = smartcar.Vehicle(vehicle_ids[0], access['access_token'])

    # Accessing car's data
    info = vehicle.info()
    battery_level = vehicle.battery()
    current_location = vehicle.location()
    odometer = vehicle.odometer()

    # Formatting the data
    converted_battery = battery_level["data"]["percentRemaining"] * 100
    converted_odometer = odometer["data"]["distance"] * 0.621371
    converted_location_latitude = current_location["data"]["latitude"]
    converted_location_longitude = current_location["data"]["longitude"]

    print(info, battery_level, current_location, odometer)

    # Render the page with formatted data
    return render_template('home.html', battery_level = converted_battery, odometer = converted_odometer, location_latitude = converted_location_latitude, location_longitude = converted_location_longitude)

# Lock the vehicle
@app.route('/lock', methods=['POST'])
def lock():
    global access
    # the list of vehicle ids
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']

    # instantiate the first vehicle in the vehicle id list
    vehicle = smartcar.Vehicle(vehicle_ids[0], access['access_token'])
    vehicle.lock()
    return redirect('/vehicle')

# Unlock the vehicle
@app.route('/unlock', methods=['POST'])
def unlock():
    global access
    # the list of vehicle ids
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']

    # instantiate the first vehicle in the vehicle id list
    vehicle = smartcar.Vehicle(vehicle_ids[0], access['access_token'])
    vehicle.unlock()
    return redirect('/vehicle')

if __name__ == '__main__':
    app.run(port=8000)