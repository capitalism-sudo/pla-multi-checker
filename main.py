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

@app.route('/read-mmos', methods=['POST'])
def read_mmos():
    results = pla.get_all_map_mmos(reader, request.json['rolls'])
    return { "mmo_spawns": results }

@app.route('/read-maps', methods=['GET'])
def read_maps():
    results = pla.get_all_map_names(reader)
    outbreaks = pla.get_all_outbreak_names(reader)
    return { "maps": results, "outbreaks": outbreaks }

@app.route('/read-one-map', methods=['POST'])
def read_one_map():
   results = pla.get_map_mmos(reader,request.json['mapname'],request.json['rolls'])
   return { "mmo_spawn": results }

@app.route('/read-normals', methods=['POST'])
def read_normals():
   results = pla.read_normal_outbreaks(reader,request.json['rolls'])
   return { "normal_spawns": results }

@app.route('/teleport-to-spawn', methods=['POST'])
def teleport():
   pla.teleport_to_spawn(reader,request.json['x'],request.json['y'],request.json['z'])

if __name__ == '__main__':
    app.run(host="localhost", port=8100, debug=True)
