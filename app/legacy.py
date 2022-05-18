from flask import request
import pla

def legacy_get_from_seed():
    try:
        group_seed = int(request.json['seed'])
    except ValueError:
        # Return an error when error handling implemented
        # return { "error": "You need to input a number for the seed" }
        return { "mmo_spawns": [] }
    results = pla.check_mmo_from_seed(group_seed,
                                  None,
                                  request.json['frencounter'],
                                  request.json['brencounter'],
                                  request.json['isbonus'],
                                  request.json['frspawns'],
                                  request.json['brspawns'],
                                  request.json['rolls'])
    return { "mmo_spawns": results }

def legacy_get_alpha_from_seed():
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
    if len(results) > 0:
        return { "alpha_spawns": results[0] }
    else:
        return { "alpha_spawns": {
            "spawn": True,
            "adv": 50000,
            "ivs": [0,0,0,0,0,0],
            "gender": -1,
            "nature": "N/A",
            "sprite": "c_0.png",
            "species": "Not Found Within 50,000 advances"
            }
        }

def legacy_check_multiseed():
    try:
        group_seed = int(request.json['seed'])
    except ValueError:
        return { "multi_spawns": {} }
    results = pla.check_multi_spawner_seed(group_seed,
                                           None,
                                           request.json['group_id'],
                                           request.json['maxalive'],
                                           request.json['maxdepth'],
                                           request.json['isnight'],
                                           request.json['rolls'])

    results_dict = {}
    for i, res in enumerate(results):
        res['adv'] = len(res['path'])
        if len(res['path']) == 0:
            res['path'] = 'Initial Spawn'
            results_dict[i] = res
    
    return { "multi_spawns": results_dict }