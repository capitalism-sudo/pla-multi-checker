import json
from pla.filters import is_shiny

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

# functions for manipulating data returned by search functions
def flatten_all_map_mmo_results(results, filter_results=True, filter_function=is_shiny):
    res = []

    for map_results in results.values():
        res.extend(flatten_map_mmo_results(map_results, filter_results, filter_function))

    return res

def flatten_map_mmo_results(results, filter_results=True, filter_function=is_shiny):
    res = []

    for key, round in results.items():
        if key[-5:] == "bonus":
            res.extend(flatten_bonusround(round, filter_results, filter_function))
        else:
            res.extend(flatten_firstround(round, filter_results, filter_function))

    return res

def flatten_normal_outbreaks(results, filter_results=True, filter_function=is_shiny):
    # It's not a bonus round, but seems to have the same shape as one
    return flatten_bonusround(results, filter_results, filter_function)

def flatten_firstround(round, filter_results, filter_function):
    if filter_results:
        return [p for p in round.values() if filter_function(p)]
    else:
        return [p for p in round.values()]

def flatten_bonusround(round, filter_results, filter_function):
    if filter_results:
        return [p for b in round.values() for p in b.values() if filter_function(p)]
    else:
        return [p for b in round.values() for p in b.values()]

def flatten_multi(results, filter_results=True, filter_function=is_shiny):
    if filter_results:
        return list(filter(filter_function, results))
    else:
        return results