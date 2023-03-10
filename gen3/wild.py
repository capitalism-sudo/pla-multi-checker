import numpy as np
from numba_pokemon_prngs.lcrng import PokeRNGDiv
from numba_pokemon_prngs.enums import Game,Lead,Encounter,Method
from numba_pokemon_prngs.data.encounter.encounter_area_3 import EncounterArea3,Slot3
from numba_pokemon_prngs.data.encounter import *
from numba_pokemon_prngs.data import SPECIES_EN, CONSTANT_CASE_SPECIES_EN, GENDER_SYMBOLS, TYPES_EN, ABILITIES_EN, NATURES_EN
from numba_pokemon_prngs.gen3.wild_generator_3 import WildGenerator3
import json
from enum import Enum

#imports from main.py
from app import RESOURCE_PATH
from gen3.core import *
from gen3.filters import compare_all_ivs
from gen3.data import natures, pktype, getSlotRanges, calcCharm, setLevel,get_bdsp_sprite


enctypetomap = {
    "Grass":"land_mons",
    "RockSmash":"rock_smash_mons",
    "OldRod":"fishing_mons",
    "GoodRod":"fishing_mons",
    "SuperRod":"fishing_mons",
    "Surfing":"water_mons"
}

def populate_routes(gamever,enctype):

    locations = []

    map_names = MAP_NAMES_GEN3[Game(1 << gamever)]

    for i,value in enumerate(map_names):
        info = {
            "location": value,
            "rawloc": i,
        }
        locations.append(info)
    
    return locations

    '''

    type = enctypetomap[enctype]

    encounters = json.load(open(f"./static/resources/gen3/{gamever}_encounter.json"))

    locations = []

    for _,l in enumerate(encounters["encounters"]):
        if l.get(type) is not None:
            info = {
                "location":l["map"].replace("MAP_", '').replace("_", " ").replace("ROUTE", "ROUTE ").title(),
                "rawloc":l["map"]
            }
            locations.append(info)

    return locations
    '''

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

    for slot_id,slot in enumerate(table):
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
    '''
    type = enctypetomap[enctype]

    encounters = json.load(open(f"./static/resources/gen3/{gamever}_encounter.json"))

    species = []
    table = None

    for _,l in enumerate(encounters["encounters"]):
        if l["map"] == location:
            table = l
            break

    for _,s in enumerate(table[type]["mons"]):
        dupe = False
        for _,i in enumerate(species):
            if i.get("raws", None) == s['species']:
                dupe = True
                break
        if not dupe:
            info = {
                "species":s["species"].replace("SPECIES_", '').title(),
                "raws":s["species"]
            }
            species.append(info)
    
    return species
    '''

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
    '''

    type = enctypetomap[enctype]

    encounters = json.load(open(f"./static/resources/gen3/{gamever}_encounter.json"))

    for _,l in enumerate(encounters["encounters"]):
        if l["map"] == location:
            table = l
            break
    
    for i,s in enumerate(table[type]["mons"]):
        if s["species"] == species:
            slots.append(i)

    return slots
    '''

def check_wilds(tid,sid,filter,delay,method,lead,encounter,rseSafari,rock,leadopt = "None",seed=0):

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


    '''
    type = enctypetomap[encounter["type"]]
    genc = json.load(open(f"./static/resources/gen3/{encounter['version']}_encounter.json"))
    table = None

    for _,l in enumerate(genc["encounters"]):
        if l["map"] == encounter["loc"]:
            table = l
            break


    tid = int(tid)
    sid = int(sid)
    tsv = tid ^ sid

    seed = int(seed,16)

    init = PokeRNGDiv(seed)
    init.advance(filter['minadv']+delay)

    cuteCharmFlag = False
    sync = False

    for i in range(0,filter['maxadv']+1):

        rng = PokeRNGDiv(init.seed)

        if encounter['type'] == "RockSmash":
            if rseSafari or not rock:
                rng.next()
            rockenccheck = rng.next_u16() % 2880
            if (rockenccheck) >= (table[type]['encounter_rate'] * 16):
                init.next()
                continue

            slot = getSlotRanges(rng.next_u16(),"RockSmash")
            level,species = setLevel(slot, rng.next_u16(), table[type])

            if rseSafari:
                rng.advance(1)
        elif encounter['type'] == "Grass":

            rng.next()
            slot = getSlotRanges(rng.next_u16(),"Grass")
            level,species = setLevel(slot, rng.next_u16(), table[type])

            if rseSafari:
                rng.next()

        elif encounter['type'] in ["Surfing", "OldRod", "GoodRod", "SuperRod"]:

            rng.next()
            
            slot = getSlotRanges(rng.next_u16(), encounter['type'])
            level,species = setLevel(slot, rng.next_u16(), table[type])

            if encounter['type'] == "GoodRod":
                slot -= 2
            elif encounter['type'] == "SuperRod":
                slot -= 5

            if rseSafari:
                rng.next()
        else:
            slot = 0
            level = 0
            species = "Egg"
        
        if lead == "None":
            nature = natures(rng.next_u16() % 25)
        elif lead == "Synch":
            if (rng.next_u16() & 1) == 0:
                #sync nature
                nature = leadopt
                sync = True
            else:
                #sync failed
                nature = natures(rng.next_u16() % 25)
        else:
            #covers Cute Charm
            cuteCharmFlag = (rng.next_u16() % 3) > 0
            nature = natures(rng.next_u16() % 25)

            #now search for PID that matches hunt nature
            
            while True:
                low = rng.next_u16()
                high = rng.next_u16()
                pid = setPID(high,low)
                if not ((pid % 25 != nature) or (cuteCharmFlag and not calcCharm(lead,pid))):
                    break
    

        low = rng.next_u16()
        high = rng.next_u16()
        pid = setPID(high,low)
        testnature = natures(pid%25)
        testcalccharm = calcCharm(leadopt,pid)
        while (natures(pid % 25) != nature) or (cuteCharmFlag and not calcCharm(leadopt,pid)):
            testnature = natures(pid%25)
            testcalccharm = calcCharm(leadopt,pid)
            low = rng.next_u16()
            high = rng.next_u16()
            pid = setPID(high,low)
        
        ability = pid & 1
        gender = pid & 255
        shiny,square = setShiny(tsv,high^low)

        if method == 1:
            iv1 = rng.next_u16()
            iv2 = rng.next_u16()
        elif method == 2:
            rng.next()
            iv1 = rng.next_u16()
            iv2 = rng.next_u16()
        else:
            iv1 = rng.next_u16()
            rng.next()
            iv2 = rng.next_u16()
        
        ivs = setIVs(iv1,iv2)
        hidden,power = calcHiddenPower(ivs)

        info = {
            "shiny": shiny,
            "square": square,
            "hidden": pktype(hidden),
            "power": power,
            "ability": ability,
            "nature": nature,
            "pid": pid,
            "gender": gender,
            "adv": i+filter['minadv'],
            "ivs": ivs,
            "slot": slot,
            "sync": sync,
            "level": level,
            "species": species,
            "sprite": get_bdsp_sprite(SPECIES.index(species),shiny)
        }

        if compare_all_ivs(filter['minivs'], filter['maxivs'], ivs):
            result[i] = info
    
        init.next()

    return result
    '''