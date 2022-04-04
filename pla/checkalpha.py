# Go to root of PyNXReader
import sys
import json
from .xoroshiro import XOROSHIRO

with open("./static/resources/text_natures.txt",encoding="utf-8") as text_natures:
    NATURES = text_natures.read().split("\n")

with open("./static/resources/text_species_en.txt",encoding="utf-8") as text_species:
    SPECIES = text_species.read().split("\n")

def generate_from_seed(seed,rolls,guaranteed_ivs=0,set_gender=False):
    rng = XOROSHIRO(seed)
    ec = rng.rand(0xFFFFFFFF)
    sidtid = rng.rand(0xFFFFFFFF)
    for _ in range(rolls):
        pid = rng.rand(0xFFFFFFFF)
        shiny = ((pid >> 16) ^ (sidtid >> 16) \
            ^ (pid & 0xFFFF) ^ (sidtid & 0xFFFF)) < 0x10
        if shiny:
            break
    ivs = [-1,-1,-1,-1,-1,-1]
    for i in range(guaranteed_ivs):
        index = rng.rand(6)
        while ivs[index] != -1:
            index = rng.rand(6)
        ivs[index] = 31
    for i in range(6):
        if ivs[i] == -1:
            ivs[i] = rng.rand(32)
    ability = rng.rand(2) # rand(3) if ha possible
    if set_gender:
        gender = -1
    else:
        gender = rng.rand(252) + 1
    nature = rng.rand(25)
    return ec,pid,ivs,ability,gender,nature,shiny

def slot_to_pokemon(values,slot):
    """Compare slot to list of slots to find pokemon"""
    for pokemon,slot_value in values.items():
        if slot <= slot_value:
            return pokemon
        slot -= slot_value
    return None

def find_slots(isnight,spawnerinfo):
    print(f"Spawnerinfo: {spawnerinfo}")
    for time_weather, values in spawnerinfo.items():
        slot_time,slot_weather = time_weather.split("/")
        if (isnight and slot_time in ("Any Time", "Night")) or (not isnight and slot_time in ("Any Time", "Day")):
            return values
    return None

def find_slot_range(isnight,species,spawnerinfo):
    values = find_slots(isnight,spawnerinfo)
    pokemon = list(values.keys())
    slot_values = list(values.values())
    if not species in pokemon:
        return 0,0,0
    start = sum(slot_values[:pokemon.index(species)])
    end = start + values[species]
    return start,end,sum(slot_values)

def check_alpha_from_seed(group_seed,rolls,isalpha,set_gender,pfilter):
    print(f"Rolls: {rolls} Is Alpha? {isalpha} Set Gender? {set_gender}")
    if pfilter["species"] == "" or pfilter["mapname"] == "" or pfilter["spawner"] == "":
        encsum = 0
        encslotmin = 0
        encslotmax = 0
    else:
        sp_slots = json.load(open(f"./static/resources/{pfilter['mapname']}.json"))
        spawnerinfo = sp_slots.get(pfilter["spawner"],None)
        if spawnerinfo is None:
            encslotmin,encslotmax,encsum = 0,0,0
        else:
            encslotmin,encslotmax,encsum = find_slot_range(pfilter["daynight"], pfilter["species"], spawnerinfo)
    guaranteed_ivs = 3 if isalpha else 0
    main_rng = XOROSHIRO(int(group_seed))
    adv = -1
    while True:
        adv += 1
        rng = XOROSHIRO(*main_rng.seed.copy())
        spawner_seed = rng.next()
        rng = XOROSHIRO(spawner_seed)
        #print(f"Encmin: {encslotmin}, Encmax: {encslotmax}, Encsum: {encsum}")
        encslot = (rng.next() / (2**64)) * encsum
        #print(f"Encslot: {encslot}")
        fixed_seed = rng.next()
        ec,pid,ivs,ability,gender,nature,shiny = \
            generate_from_seed(fixed_seed,rolls,guaranteed_ivs,set_gender)
        if shiny and encslot <= encslotmax and encslot >= encslotmin:
            break
        if adv > 50000:
            break
        main_rng.next()
        main_rng.next()
        main_rng = XOROSHIRO(main_rng.next())

    form = ''
    if encslotmax is 0 or encsum is 0:
        cutspecies = "Egg"
    elif "Alpha" in pfilter["species"] and "-" in pfilter["species"]:
        cutspecies = pfilter["species"].rpartition('Alpha')[2]
        form = pfilter["species"].rpartition('-')[2]
        cutspecies = cutspecies.rpartition('-')[0]     
    elif "Alpha" in pfilter["species"]:
        cutspecies = pfilter["species"].rpartition('Alpha')[2]
    elif "-" in pfilter["species"]:
        cutspecies = pfilter["species"].rpartition('-')[0]
        form = pfilter["species"].rpartition('-')[2]
    elif pfilter["species"] != "":
        cutspecies = pfilter["species"]
    else:
        cutspecies = "Egg"

    if adv <= 50000:
        results = {
            "spawn": True,
            "adv": adv,
            "ivs": ivs,
            "gender": gender,
            "nature": NATURES[nature],
            "sprite": f"c_{SPECIES.index(cutspecies)}" + f"{f'-{form}' if len(form) != 0 else ''}s.png",
            "species": pfilter["species"]
            }
    else:
        results = {
            "spawn": True,
            "adv": adv,
            "ivs": [0,0,0,0,0,0],
            "gender": -1,
            "nature": "N/A",
            "sprite": "c_0.png",
            "species": "Not Found Within 50,000 advances"
            }

    return results


