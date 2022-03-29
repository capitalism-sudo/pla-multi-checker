import signal
import json

from flask import Flask, render_template, request
from nxreader import NXReader
import pla

app = Flask(__name__)

config = json.load(open("config.json"))
if config["SeedCheckOnly"]:
   print("Seed Check only mode! Note: You will not be able to use MMO checker or Distiortion Checker!")
else:
   reader = NXReader(config["IP"], usb_connection=config["USB"])

   def signal_handler(signal, advances): #CTRL+C handler
      print("Stop request")
      reader.close()

   signal.signal(signal.SIGINT, signal_handler)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/mmos")
def mmo_checker():
   return render_template('mmo-checker.html')

@app.route("/distortion")
def distortion():
   return render_template('distortion.html')

@app.route("/seed")
def seed():
   return render_template('fromseed.html')

@app.route('/read-mmos', methods=['POST'])
def read_mmos():
    #results = pla.get_all_map_mmos(reader, request.json['rolls'], request.json['inmap'])
   results = pla.get_all_map_mmos(reader, request.json['rolls'], False)
   return { "mmo_spawns": results }

@app.route('/read-maps', methods=['GET'])
def read_maps():
    results = pla.get_all_map_names(reader)
    outbreaks = pla.get_all_outbreak_names(reader,False)
    return { "maps": results, "outbreaks": outbreaks }

@app.route('/read-one-map', methods=['POST'])
def read_one_map():
   #results = pla.get_map_mmos(reader,request.json['mapname'],request.json['rolls'], request.json['inmap'])
   results = pla.get_map_mmos(reader,request.json['mapname'],request.json['rolls'], False)
   return { "mmo_spawn": results }

@app.route('/read-normals', methods=['POST'])
def read_normals():
   #results = pla.read_normal_outbreaks(reader,request.json['rolls'],request.json['inmap'])
   results = pla.read_normal_outbreaks(reader,request.json['rolls'],False)
   return { "normal_spawns": results }

@app.route('/teleport-to-spawn', methods=['POST'])
def teleport():
   pla.teleport_to_spawn(reader,request.json['coords'])
   return ""

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

@app.route('/check-mmoseed', methods=['POST'])
def get_from_seed():
   results = pla.check_from_seed(request.json['seed'],
                                 request.json['rolls'],
                                 request.json['frencounter'],
                                 request.json['brencounter'],
                                 request.json['isbonus'],
                                 request.json['frspawns'],
                                 request.json['brspawns'])
   return { "mmo_spawns": results }

if __name__ == '__main__':
    app.run(host="localhost", port=8100, debug=True)
