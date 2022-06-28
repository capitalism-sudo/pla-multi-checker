from numpy import true_divide
from pla.rng import XOROSHIRO,OverworldRNG,Filter
from app import RESOURCE_PATH
from pla.data import natures
import json

from pla.rng.owrng import OverworldState

encounters = json.load(open("./static/resources/SWSH_Encounters.json"))
personal = json.load(open("./static/resources/SWSH_Personal.json"))

with open(RESOURCE_PATH + "resources/text_species_en.txt",encoding="utf-8") as text_species:
    SPECIES = text_species.read().split("\n")

def populate_location(type,version):


    locations = [l for l in encounters[version][type]]

    return locations

def populate_weather(location,type,version):

    weather = [w for w in encounters[version][type][location]]

    return weather

def populate_species(weather,location,type,version):

    pull = encounters[version][type][location][weather]
    if type != "Static":
        pull = pull["Slots"]
    species = [s for s in pull]

    return species

def autofill(weather,location,type,version,species):

    egg_move_var = 0
    min_slot = 0
    max_slot = 0
    forced_ability_var = 0
    flawless_ivs = 0

    if type != "Static" and personal[species]["Item"]:
        held_item = True
    else:
        held_item = False

    if type != "Static":
        egg_move_var = len(personal[species]["Egg_Moves"])
    
    min_level = max_level = 0

    if type != "Static":
        min_level,max_level = encounters[version][type][location][weather]["Level"]
    else:
        min_level = max_level = encounters[version][type][location][weather][species]["Level"]
        forced_ability_var = -1 if encounters[version][type][location][weather][species]["Ability"] == -1 else encounters[version][type][location][weather][species]["Ability"]

    if type != "Static":
        min_slot,max_slot = encounters[version][type][location][weather]["Slots"][species]
        flawless_ivs = 0
    else:
        flawless_ivs = encounters[version][type][location][weather][species]["GuaranteedIVs"]
    
    if species in ["Articuno-1", "Zapdos-1", "Moltres-1", "Keldeo-1"]:
        shiny_locked = True
    else:
        shiny_locked = False
    
    info = {
        "minslot": min_slot,
        "maxslot": max_slot,
        "minlevel": min_level,
        "maxlevel": max_level,
        "eggmove": egg_move_var,
        "helditem": held_item,
        "ivs": flawless_ivs,
        "shinylockeix": shiny_locked,
        "forced_ability": forced_ability_var
    }

    return info

def get_sprite(info, result: OverworldState):

    species = 0

    if result.is_static:
        species = SPECIES.index(info['species'])
    else:
        specnames = encounters[info['version']][info['type']][info['loc']][info['weather']]["Slots"]
        for value in specnames:
            form = ''
            if '-' in value:
                noformvalue = value.rpartition('-')[0]
                form = value.rpartition('-')[2]
            else:
                noformvalue = value
            if result.slot_rand in range(specnames[value][0], specnames[value][1]+1):
                species = SPECIES.index(noformvalue)
                return f"c_{species}{f'-{form}' if form != '' else ''}{'s' if result.xor <= 16 else ''}.png"
    
    return f"c_{species}{f'-{form}' if form != '' else ''}{'s' if result.xor <= 16 else ''}.png"

def get_species_name(info, result: OverworldState):

    species = "Egg"

    if result.is_static:
        species = info['species']
    else:
        specnames = encounters[info['version']][info['type']][info['loc']][info['weather']]["Slots"]
        for value in specnames:
            if result.slot_rand in range(specnames[value][0], specnames[value][1]+1):
                species = value
    
    return species

def check_overworld_seed(states, filter: Filter, owoptions, initadv, maxadv, info):
    
    res = {}

    for i in range(len(states)):
        states[i] = int(states[i],16)

    rng = XOROSHIRO(*states)

    predict = OverworldRNG(
        seed = rng.state,
        tid = int(owoptions['tid']),
        sid = int(owoptions['sid']),
        shiny_charm = owoptions['shiny_charm'],
        mark_charm = owoptions['mark_charm'],
        weather_active = owoptions['weather_active'],
        is_fishing = owoptions['is_fishing'],
        is_shiny_locked = owoptions['is_shiny_locked'],
        min_level = int(owoptions['min_level']),
        max_level = int(owoptions['max_level']),
        flawless_ivs = int(owoptions['flawless_ivs']),
        forced_ability = int(owoptions['forced_ability']),
        diff_held_item = owoptions['diff_held_item'],
        egg_move_count = int(owoptions['egg_move_count']),
        kos = int(owoptions['kos']),
        cute_charm = None if owoptions['cute_charm'] == "None" else int(owoptions['cute_charm']),
        is_static = owoptions['is_static'],
        filter = filter,
        set_gender = owoptions['set_gender'],
        is_hidden = owoptions['is_hidden']
    )

    predict.advance_fast(initadv)

    for i in range(0,maxadv-initadv):
        result = predict.generate()
        if result is not None:
            res[i] = {
                "ability": result.ability,
                "advances": result.advance,
                "brilliant": result.brilliant,
                "ec": result.ec,
                "fixed_seed": result.fixed_seed,
                "gender": result.gender,
                "height": result.height,
                "ivs": result.ivs,
                "level": result.level,
                "mark": "None" if result.mark is None else result.mark,
                "nature": natures(result.nature),
                "pid": result.pid,
                "slot_rand": result.slot_rand,
                "weight": result.weight,
                "xor": result.xor,
                "shiny": True if result.xor <= 16 else False,
                "square": True if result.xor == 0 else False,
                "sprite": get_sprite(info, result),
                "species": get_species_name(info, result)
            }
    

    return res