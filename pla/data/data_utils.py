import json

# These are utility functions for understanding PLA data that are not generally used in the app
map_names = ['AlabasterIcelands', 'CobaltCoastlands', 'CoronetHighlands', 'CrimsonMirelands', 'ObsidianFieldlands']

def encounter_names(map_name):
    """Get a set of all the pokemon that are encountered on the map"""
    m1 = json.load(open(f'static/resources/{map_name}.json'))
    m2 = [m.values() for m in m1.values()]
    m3 = [b.keys() for a in m2 for b in a]
    m4 = [b for a in m3 for b in a]
    return set(m4)

def all_encounter_names():
    """Get a set of all the pokemon encountered on all maps"""
    res = set()
    for m in map_names:
        res.update(encounter_names(m))
    return res

def all_mmo_pokemon():
    """Get a set all pokemon that are enountered in mmos"""
    mmo = json.load(open(f'static/resources/mmo_es.json'))
    return set([m['name'] for b in mmo.values() for m in b])