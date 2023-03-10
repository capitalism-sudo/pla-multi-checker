
from numba_pokemon_prngs.enums import Game,Lead,Encounter,Method
from numba_pokemon_prngs.data.encounter.encounter_area_3 import EncounterArea3
from numba_pokemon_prngs.data.encounter import *
from numba_pokemon_prngs.data import SPECIES_EN, TYPES_EN, ABILITIES_EN, NATURES_EN
from numba_pokemon_prngs.gen3.wild_generator_3 import WildGenerator3

#imports from main.py
from gen3.core import *
from gen3.filters import compare_all_ivs
from gen3.data import get_bdsp_sprite


def populate_routes(gamever):

    locations = []

    map_names = MAP_NAMES_GEN3[Game(1 << gamever)]

    for i,value in enumerate(map_names):
        info = {
            "location": value,
            "rawloc": i,
        }
        locations.append(info)
    
    return locations

def populate_species(gamever,enctype,location):

    species = []

    encounter_info: EncounterArea3 = ENCOUNTER_INFORMATION_GEN3[Game(1 << gamever)][location]

    encounter_type: Encounter = Encounter(enctype)


    if encounter_type == Encounter.GRASS:
        table = encounter_info.land
    elif encounter_type == Encounter.ROCK_SMASH:
        table = encounter_info.rock
    elif encounter_type == Encounter.SURFING:
        table = encounter_info.water
    elif encounter_type == Encounter.OLD_ROD:
        table = encounter_info.fish_old
    elif encounter_type == Encounter.GOOD_ROD:
        table = encounter_info.fish_good
    else:
        table = encounter_info.fish_super

    for _,slot in enumerate(table):
        dupe = False
        species_name = SPECIES_EN[slot.species]
        if species_name == "Egg":
            return {
                "species": "None",
                "raws": "None",
            }
        for _, i in enumerate(species):
            if i.get("species", None) == species_name:
                dupe = True
                break
        if not dupe:
            info = {
                "species": species_name,
                "raws": species_name,
            }
            species.append(info)
    

    return species
  
def autofill(gamever,enctype,location,species):

    if species == "any":
        return "any"
    
    slots = []

    encounter_info: EncounterArea3 = ENCOUNTER_INFORMATION_GEN3[Game(1 << gamever)][location]

    encounter_type: Encounter = Encounter(enctype)


    if encounter_type == Encounter.GRASS:
        table = encounter_info.land
    elif encounter_type == Encounter.ROCK_SMASH:
        table = encounter_info.rock
    elif encounter_type == Encounter.SURFING:
        table = encounter_info.water
    elif encounter_type == Encounter.OLD_ROD:
        table = encounter_info.fish_old
    elif encounter_type == Encounter.GOOD_ROD:
        table = encounter_info.fish_good
    else:
        table = encounter_info.fish_super

    for slot_id,slot in enumerate(table):
        if species == SPECIES_EN[slot.species]:
            slots.append(slot_id)
    
    return slots

def check_wilds(tid,sid,filter,delay,method,encounter,leadopt = 255,seed=0):

    result = {}

    #map_name = MAP_NAMES_GEN3[Game(1 << encounter['version'])][encounter['loc']]
    encounter_area: EncounterArea3 = ENCOUNTER_INFORMATION_GEN3[Game(1 << encounter['version'])][encounter['loc']]

    enc_type: Encounter = Encounter(encounter['type'])
    method_type: Method = Method(method)
    lead_type: Lead = Lead(leadopt)
    
    tid = int(tid)
    sid = int(sid)

    seed = int(seed,16)

    gen = WildGenerator3(method_type, enc_type, lead_type, Game(1 << encounter['version']), tid, sid)

    states = gen.generate(seed, delay, filter['minadv'], filter['maxadv']+1, encounter_area)

    for state in states:
        info = {
            "shiny": True if state.shiny in [1,2] else False,
            "square": True if state.shiny == 2 else False,
            "hidden": TYPES_EN[state.hidden_power+1],
            "power": state.hidden_power_strength,
            "ability": ABILITIES_EN[state.ability_index],
            "nature": NATURES_EN[state.nature],
            "pid": state.pid,
            "gender": state.gender,
            "adv": state.advance,
            "ivs": state.ivs.tolist(),
            "level": state.level,
            "species": SPECIES_EN[state.species],
            "sprite": get_bdsp_sprite(state.species,True if state.shiny in [1,2] else False)
        }

        if compare_all_ivs(filter['minivs'], filter['maxivs'], state.ivs):
            result[state.advance] = info
    
    return result