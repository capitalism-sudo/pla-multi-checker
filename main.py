import signal
import json

from flask import Flask, render_template, request
from nxreader import NXReader
import pla

app = Flask(__name__)

config = json.load(open("config.json"))
reader = NXReader(config["IP"], usb_connection=config["USB"])

def signal_handler(signal, advances): #CTRL+C handler
   print("Stop request")
   reader.close()

signal.signal(signal.SIGINT, signal_handler)

@app.route("/")
def home():
    return render_template('index.html')

@app.route('/read-distortions', methods=['POST'])
def read_distortions():
    results = pla.check_all_distortions(reader, request.json['map_name'], request.json['rolls'])
    return { "distortion_spawns": results }

@app.route('/create-distortion', methods=['POST'])
def create_distortion():
    pla.create_distortion(reader)
    return "Distortion Created"

@app.route('/map-info', methods=['POST'])
def get_map_info():
    locations = pla.get_distortion_locations(request.json['map_name'])
    spawns = pla.get_distortion_spawns(request.json['map_name'])
    return { "locations": locations, "spawns": spawns }

if __name__ == '__main__':
    app.run(host="localhost", port=8100, debug=True)