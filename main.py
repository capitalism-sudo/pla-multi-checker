import signal
import json

from flask import Flask, render_template, request
from nxreader import NXReader
import pla
from pla.data import Pokedex
from pla.saves import read_research, rolls_from_research

app = Flask(__name__)

# Set max size for uploads
app.config['MAX_CONTENT_LENGTH'] = 2 * 1000 * 1000

# Load a Pokdex
pokedex = Pokedex()
hisuidex = pokedex.hisuidex()

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
   return render_template('pages/mmos.html', title='MMO Checker')

@app.route("/distortions")
def distortion():
   return render_template('pages/distortions.html', title='Distortion Checker')

@app.route("/seeds")
def seed():
   return render_template('pages/seeds.html', title='MMO Checker')

@app.route("/spawns")
def alpha():
   return render_template('pages/spawns.html', title='Spawn Checker')

@app.route("/multis")
def multi():
   return render_template('pages/multis.html', title='Multi Spawn Checker')

@app.route("/multiseed")
def multiseed():
   return render_template('pages/multiseed.html', title='Multi Spawn Seed Checker')

@app.route("/settings")
def settings():
   return render_template('pages/settings.html', title='Settings')

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

@app.route('/check-alphaseed', methods=['POST'])
def get_alpha_from_seed():
   results = pla.check_alpha_from_seed(request.json['seed'], request.json['rolls'],
                                       request.json['isalpha'], request.json['setgender'],
                                       request.json['filter'])
   return { "alpha_spawns": results }

@app.route('/check-multi-spawn', methods=['POST'])
def check_multispawner():
   results = pla.check_multi_spawner(reader, request.json['rolls'], request.json['group_id'], request.json['maxalive'],request.json['maxdepth'])

   return { "multi_spawns": results }

@app.route('/check-multi-seed', methods=['POST'])
def check_multiseed():
   results = pla.check_multi_spawner_seed(request.json['seed'], request.json['rolls'], request.json['group_id'], request.json['maxalive'],request.json['maxdepth'])

   return { "multi_spawns": results}

@app.route('/api/hisuidex')
def pokemon():
    return { 'hisuidex': hisuidex }

@app.route('/api/read-research', methods=['POST'])
def read_savefile():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'save' not in request.files:
            return { 'error': 'There was no save file selected' }
        save = request.files['save']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if save.filename == '':
            return { 'error': 'There was no save file selected' }

        if save:
            savedata = bytearray(save.read());
            results = read_research(savedata)
            if 'error' in results:
                return { 'error': results['error'] }

            rolls = { pkm['name'] : rolls_from_research(results['research_entries'], pkm) for pkm in hisuidex}
            
            return {
                'shinycharm': results['shinycharm'],
                'rolls': rolls
            }
    
    return { 'error': 'There was a problem reading your save' }

if __name__ == '__main__':
    app.run(host="localhost", port=8100, debug=True)
