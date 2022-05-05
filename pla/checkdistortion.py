import json
from ast import literal_eval
from app import RESOURCE_PATH
from pla.core import BASE_ROLLS, generate_from_seed, get_rolls, get_sprite
from pla.data import pokedex, natures
from pla.rng import XOROSHIRO

distortions = json.load(open(RESOURCE_PATH + "resources/distortions.json"))

distortion_offset = {
    "obsidianfieldlands": 0x990,
    "crimsonmirelands": 0xC78,
    "cobaltcoastlands": 0xCC0,
    "coronethighlands": 0x818,
    "alabastericelands": 0x948
}

def read_wild_rng(map_name, index, group_seed, research, rolls_override = None):
    rng = XOROSHIRO(group_seed)
    spawner_seed = rng.next()
    rng = XOROSHIRO(spawner_seed)
    
    encounter_slot = (rng.next()/(2**64)) * get_encounter_slot_max(map_name, index)
    pokemon, alpha = get_encounter(map_name, encounter_slot)
    rolls = rolls_override if rolls_override is not None else get_rolls(pokemon, research, BASE_ROLLS)
    fixed_seed = rng.next()
    
    ec,pid,ivs,ability,gender,nature,shiny,square = \
        generate_from_seed(fixed_seed, rolls, 3 if alpha else 0, pokemon.is_fixed_gender())
    
    gender = pokemon.calculate_gender(gender)
        
    return fixed_seed, encounter_slot, rolls, pokemon, ec, pid, ivs, ability, gender, nature, shiny, square, alpha

def get_generator_seed(reader, map_name, distortion_index):
    return reader.read_pointer_int(f"[[[[[[main+42CC4D8]+C0]+1C0]+{distortion_offset[map_name] + distortion_index * 0x8:X}]+18]+430]+C0", 8)

def get_distortion_spawns(map_name):
    return [s['species'] for s in distortions[map_name]['encounters'] if s['alpha'] == False]

def get_distortion_locations(map_name):
    return [loc for loc in distortions[map_name]['locations'].values() if loc.lower() != "unknown"]

def get_distortion_location(map_name, distortion_index):
    for location in distortions[map_name]['locations']:
        start, end = literal_eval(location)
        if distortion_index >= start and distortion_index < end:
            return  distortions[map_name]['locations'][location]

def get_encounter_slot_max(map_name, distortion_index):
    if map_name == 'crimsonmirelands' and distortion_index >= 13 and distortion_index < 16:
        return distortions['crimsonmirelands']['encounter_slot_max_ursas_ring']

    return distortions[map_name]['encounter_slot_max']

def get_encounter(map_name, encounter_slot):
    for encounter in distortions[map_name]['encounters']:
        if encounter['min'] < encounter_slot and encounter_slot <= encounter['max']:
            return pokedex.entry(encounter['species']), encounter['alpha']

def is_common_spawn(distortion_index, distortion_name):
    return distortion_index in [0,4,8,12,16,20] or distortion_name.lower() == "unknown"

def check_all_distortions(reader, map_name, research, rolls_override = None):
    return list(filter(None, (check_distortion(reader, map_name, i, research, rolls_override) for i in range(distortions[map_name]['number']))))

def check_distortion(reader, map_name, distortion_index, research, rolls_override = None):
    distortion_name = get_distortion_location(map_name, distortion_index)
    generator_seed = get_generator_seed(reader, map_name, distortion_index)
    
    if generator_seed == 0 or is_common_spawn(distortion_index, distortion_name):
        return None

    group_seed = (generator_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF
    fixed_seed, encounter_slot, rolls, pokemon, ec, pid, ivs, ability, gender, nature, shiny, square, alpha = \
            read_wild_rng(map_name, distortion_index, group_seed, research, rolls_override)
    
    return {
        "index": distortion_index,
        "generator_seed": generator_seed,
        "distortion_name": distortion_name,
        "encounter_slot": encounter_slot,
        "species": pokemon.display_name(),
        "sprite": get_sprite(pokemon, shiny, gender),
        "ec": ec,
        "pid": pid,
        "ivs": ivs,
        "ability": ability,
        "gender": gender.value,
        "nature": natures(nature),
        "shiny": shiny,
        "square": square,
        "alpha": alpha,
        "rolls": rolls
    }
