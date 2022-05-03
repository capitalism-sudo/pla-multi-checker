import signal
import json
import mimetypes

from flask import Flask, render_template, request
from nxreader import NXReader
import pla
from pla.core import teleport_to_spawn
from pla.data import hisuidex
from pla.saves import read_research, rolls_from_research
from pla.data.data_utils import flatten_all_map_mmo_results, flatten_map_mmo_results, flatten_normal_outbreaks, flatten_multi

mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('application/javascript', '.mjs')

app = Flask(__name__)

# Set max size for uploads
app.config['MAX_CONTENT_LENGTH'] = 2 * 1000 * 1000

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


# API ROUTES
@app.route('/api/read-mmos', methods=['POST'])
def read_mmos():
    results = pla.get_all_map_mmos(reader, request.json['rolls'], False)
    return { "results": flatten_all_map_mmo_results(results, config.get('FILTER_ON_SERVER', False)) }

@app.route('/api/read-one-map', methods=['POST'])
def read_one_map():
    results = pla.get_map_mmos(reader,request.json['mapname'],request.json['rolls'], False)
    return { "results": flatten_map_mmo_results(results, config.get('FILTER_ON_SERVER', False)) }

@app.route('/api/read-normals', methods=['POST'])
def read_normals():
    results = pla.get_all_outbreaks(reader,request.json['rolls'], False)
    return { "results": flatten_normal_outbreaks(results, config.get('FILTER_ON_SERVER', False)) }

@app.route('/api/read-maps', methods=['GET'])
def read_maps():
    map_names = pla.get_all_map_names(reader)
    outbreaks = pla.get_all_outbreak_names(reader,False)
    return { "maps": map_names, "outbreaks": outbreaks }

@app.route('/api/teleport-to-spawn', methods=['POST'])
def teleport():
    teleport_to_spawn(reader, request.json['coords'])
    return ""

@app.route('/api/read-distortions', methods=['POST'])
def read_distortions():
    results = pla.check_all_distortions(reader,
                                        request.json['map_name'],
                                        request.json['rolls'])
    return { "results": results }

@app.route('/api/create-distortion', methods=['POST'])
def create_distortion():
    pla.create_distortion(reader)
    return "Distortion Created"

@app.route('/api/map-info', methods=['POST'])
def get_map_info():
    locations = pla.get_distortion_locations(request.json['map_name'])
    spawns = pla.get_distortion_spawns(request.json['map_name'])
    return { "locations": locations, "spawns": spawns }

@app.route('/api/check-mmoseed', methods=['POST'])
def get_from_seed():
    try:
        group_seed = int(request.json['seed'])
    except ValueError:
        return { "error": "You need to input a number for the seed" }
    
    results = pla.check_mmo_from_seed(group_seed,
                                  request.json['rolls'],
                                  request.json['frencounter'],
                                  request.json['brencounter'],
                                  request.json['isbonus'],
                                  request.json['frspawns'],
                                  request.json['brspawns'])
    return { "results": flatten_map_mmo_results(results, config.get('FILTER_ON_SERVER', False)) }

@app.route('/api/check-alphaseed', methods=['POST'])
def get_alpha_from_seed():
    try:
        group_seed = int(request.json['seed'])
    except ValueError:
        return { "error": "You need to input a number for the seed" }
    
    results = pla.check_alpha_from_seed(group_seed,
                                        request.json['rolls'],
                                        request.json['isalpha'],
                                        request.json['setgender'],
                                        request.json['filter'])
    return { "results": [results] }

@app.route('/api/check-multi-spawn', methods=['POST'])
def check_multispawner():
    results = pla.check_multi_spawner(reader,
                                      request.json['rolls'],
                                      request.json['group_id'],
                                      request.json['maxalive'],
                                      request.json['maxdepth'],
                                      request.json['isnight'])
    return { "results": flatten_multi(results, config.get('FILTER_ON_SERVER', False)) }

@app.route('/api/check-multi-seed', methods=['POST'])
def check_multiseed():
    try:
        group_seed = int(request.json['seed'])
    except ValueError:
        return { "error": "You need to input a number for the seed" }

    results = pla.check_multi_spawner_seed(group_seed,
                                           request.json['rolls'],
                                           request.json['group_id'],
                                           request.json['maxalive'],
                                           request.json['maxdepth'],
                                           request.json['isnight'])
    return { "results": flatten_multi(results, config.get('FILTER_ON_SERVER', False)) }

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

# existing version of api calls, preserved in case used by external applications
@app.route('/read-mmos', methods=['POST'])
def read_mmos_old():
    #results = pla.get_all_map_mmos(reader, request.json['rolls'], request.json['inmap'])
    results = pla.get_all_map_mmos(reader, request.json['rolls'], False)
    return { "mmo_spawns": flatten_all_map_mmo_results(results, config.get('FILTER_ON_SERVER', False)) }

@app.route('/read-one-map', methods=['POST'])
def read_one_map_old():
    #results = pla.get_map_mmos(reader,request.json['mapname'],request.json['rolls'], request.json['inmap'])
    results = pla.get_map_mmos(reader,request.json['mapname'],request.json['rolls'], False)
    return { "mmo_spawn": flatten_map_mmo_results(results, config.get('FILTER_ON_SERVER', False)) }

@app.route('/read-normals', methods=['POST'])
def read_normals_old():
    #results = pla.read_normal_outbreaks(reader,request.json['rolls'],request.json['inmap'])
    results = pla.get_all_outbreaks(reader,request.json['rolls'],False)
    return { "normal_spawns": flatten_normal_outbreaks(results, config.get('FILTER_ON_SERVER', False)) }

@app.route('/read-maps', methods=['GET'])
def read_maps_old():
    results = pla.get_all_map_names(reader)
    outbreaks = pla.get_all_outbreak_names(reader,False)
    return { "maps": results, "outbreaks": outbreaks }

@app.route('/read-distortions', methods=['POST'])
def read_distortions_old():
    results = pla.check_all_distortions(reader,
                                        request.json['map_name'],
                                        request.json['rolls'])
    return { "distortion_spawns": results }

@app.route('/create-distortion', methods=['POST'])
def create_distortion_old():
    pla.create_distortion(reader)
    return "Distortion Created"

@app.route('/map-info', methods=['POST'])
def get_map_info_old():
    locations = pla.get_distortion_locations(request.json['map_name'])
    spawns = pla.get_distortion_spawns(request.json['map_name'])
    return { "locations": locations, "spawns": spawns }

@app.route('/check-mmoseed', methods=['POST'])
def get_from_seed_old():
    try:
        group_seed = int(request.json['seed'])
    except ValueError:
        # Return an error when error handling implemented
        # return { "error": "You need to input a number for the seed" }
        return { "mmo_spawns": [] }
    results = pla.check_from_seed(group_seed,
                                  request.json['rolls'],
                                  request.json['frencounter'],
                                  request.json['brencounter'],
                                  request.json['isbonus'],
                                  request.json['frspawns'],
                                  request.json['brspawns'])
    return { "mmo_spawns": flatten_map_mmo_results(results, config.get('FILTER_ON_SERVER', False)) }

@app.route('/check-alphaseed', methods=['POST'])
def get_alpha_from_seed_old():
    try:
        group_seed = int(request.json['seed'])
    except ValueError:
        # Return an error when error handling implemented
        # return { "error": "You need to input a number for the seed" }
        return { "alpha_spawns": [] }
    results = pla.check_alpha_from_seed(group_seed,
                                        request.json['rolls'],
                                        request.json['isalpha'],
                                        request.json['setgender'],
                                        request.json['filter'])
    return { "alpha_spawns": results }

@app.route('/check-multi-spawn', methods=['POST'])
def check_multispawner_old():
    results = pla.check_multi_spawner(reader,
                                      request.json['rolls'],
                                      request.json['group_id'],
                                      request.json['maxalive'],
                                      request.json['maxdepth'],
                                      request.json['isnight'])
    return { "multi_spawns": results }

@app.route('/check-multi-seed', methods=['POST'])
def check_multiseed_old():
    try:
        group_seed = int(request.json['seed'])
    except ValueError:
        # Return an error when error handling implemented
        # return { "error": "You need to input a number for the seed" }
        return { "multi_spawns": {} }
    results = pla.check_multi_spawner_seed(group_seed,
                                           request.json['rolls'],
                                           request.json['group_id'],
                                           request.json['maxalive'],
                                           request.json['maxdepth'],
                                           request.json['isnight'])
    return { "multi_spawns": results}



if __name__ == '__main__':
    app.run(host="localhost", port=8100, debug=True)
