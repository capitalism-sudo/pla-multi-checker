import json
from app import RESOURCE_PATH
from pla.core import generate_from_seed, get_sprite
from pla.data import pokedex, natures
from pla.rng import XOROSHIRO


# given the size of the json, it might be more efficient to ultimately put this in a database
# load the encounter slots for a map, caching the results for future requests
encslot_cache = {}
def load_encounter_slots(mapname):
    if mapname not in encslot_cache:
        with open(f"{RESOURCE_PATH}resources/{mapname}.json", 'r') as encfile:
            encslot_cache[mapname] = json.load(encfile)
    return encslot_cache[mapname]

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
        sp_slots = load_encounter_slots(pfilter["mapname"])
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
        ec,pid,ivs,ability,gender,nature,shiny,square = \
            generate_from_seed(fixed_seed,rolls,guaranteed_ivs,set_gender)
        if shiny and encslot <= encslotmax and encslot >= encslotmin:
            break
        if adv > 50000:
            break
        main_rng.next()
        main_rng.next()
        main_rng = XOROSHIRO(main_rng.next())

    if adv <= 50000:
        pokemon, alpha = get_pokemon_alpha(pfilter["species"], encslotmax, encsum)
        species = pokemon.display_name() if pokemon is not None else ''
        sprite = get_sprite(pokemon, shiny) if pokemon is not None else 'c_0.png'

        return [{
            "rolls": rolls,
            "adv": adv,
            "ivs": ivs,
            "gender": gender,
            "nature": natures(nature),
            "sprite": sprite,
            "species": species,
            "shiny": shiny,
            "square": square,
            "alpha": alpha
        }]
     
    return []

def get_pokemon_alpha(species, encslotmax, encsum):
    if species == "" or encslotmax == 0 or encsum == 0:
        return None, False
    if species[0:5] == "Alpha":
        return pokedex.entry(species[5:].strip()), True
    else:
        return pokedex.entry(species), False