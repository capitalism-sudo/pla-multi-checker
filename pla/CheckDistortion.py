import json
from .xoroshiro import XOROSHIRO

distortion_offset = {
    "obsidianfieldlands": 0x980,
    "crimsonmirelands": 0xC78,
    "cobaltcoastlands": 0xCC0,
    "coronethighlands": 0x828,
    "alabastericelands": 0x948
}

distortion_locations = {
    "obsidianfieldlands": {
        (0,4): "Horseshoe Plains",
        (4,8): "Windswept Run",
        (8,12): "Nature's Pantry",
        (12,16): "Sandgem Flats"
    },
    "crimsonmirelands": {
        (0,4): "Droning Meadow",
        (4,8): "Holm of Trials",
        (8,12): "Unknown",
        (12,16): "Ursa's Landing",
        (16,20): "Prairie",
        (20,24): "Gapejaw Bog"
    },
    "cobaltcoastlands": {
        (0,4): "Ginko Landing",
        (4,8): "Aipom Hill",
        (8,12): "Deadwood Haunt",
        (12,16): "Spring Path",
        (16,20): "Windbreak Stand"
    },
    "coronethighlands": {
        (0,4): "Sonorous Path",
        (4,8): "Ancient Quarry",
        (8,12): "Celestica Ruins",
        (12,16): "Primeval Grotto",
        (16,20): "Boulderoll Ravine"
    },
    "alabastericelands": {
        (0,4): "Bonechill Wastes North",
        (4,8): "Avalugg's Legacy",
        (8,12): "Bonechill Wastes South",
        (12,16): "Southeast of Arena",
        (16,20): "Heart's Crag",
        (20,24): "Arena's Approach"
    }
}

num_distortions = {
    "obsidianfieldlands": 13,
    "crimsonmirelands": 24,
    "cobaltcoastlands": 20,
    "coronethighlands": 20,
    "alabastericelands": 24
}

encounter_slot_max = {
    "obsidianfieldlands": 112,
    "crimsonmirelands": 276,
    "crimsonmirelands-ursas-landing": 118,
    "cobaltcoastlands": 163,
    "coronethighlands": 382,
    "alabastericelands": 259,
}

fixed_gender_encounters = ["Porygon", "Porygon2", "Porygon-Z", "Magnemite", "Magneton", "Magnezone"]

encounters = json.load(open("./static/resources/distortion-encounters.json"))

with open("./static/resources/text_natures.txt",encoding="utf-8") as text_natures:
    NATURES = text_natures.read().split("\n")

def generate_from_seed(seed, rolls, guaranteed_ivs=0, fixed_gender=False):
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
    ability = rng.rand(2)+1 # rand(3) if ha possible
    if fixed_gender:
        gender = -1
    else:
        gender = rng.rand(252) + 1
    nature = rng.rand(25)
    return ec, pid, ivs, ability, gender, nature, shiny

def read_wild_rng(map_name, index, group_id, rolls):
    group_seed = group_id
    main_rng = XOROSHIRO(group_seed)
 
    rng = XOROSHIRO(*main_rng.seed.copy())
    spawner_seed = rng.next()
    rng = XOROSHIRO(spawner_seed)
    encounter_slot = (rng.next()/(2**64)) * get_encounter_slot_max(map_name, index)

    species, alpha = get_encounter(map_name, encounter_slot)
    fixed_gender = species in fixed_gender_encounters

    fixed_seed = rng.next()
    ec,pid,ivs,ability,gender,nature,shiny = \
        generate_from_seed(fixed_seed, rolls, 3 if alpha else 0, fixed_gender)
        
    return group_seed, fixed_seed, encounter_slot, species, ec, pid, ivs, ability, gender, nature, shiny, alpha

def get_generator_seed(reader, map_name, index):
    return reader.read_pointer_int(f"[[[[[[main+428E268]+C0]+1C0]+{distortion_offset[map_name] + index * 0x8:X}]+18]+428]+C8", 8)

def get_distortion_location(map_name, index):
    for location in distortion_locations[map_name]:
        if index >= location[0] and index < location[1]:
            return distortion_locations[map_name][location]

def get_encounter_slot_max(map_name, index):
    max = encounter_slot_max[map_name]

    if map_name == 'crimsonmirelands' and index >= 13 and index < 16:
        max = encounter_slot_max['crimsonmirelands-ursas-landing']
    
    return max

def get_encounter(map_name, encounter_slot):
    for encounter in encounters[map_name]:
        if encounter['min'] < encounter_slot and encounter_slot <= encounter['max']:
            return encounter['species'], encounter['alpha']

def check_filter(shiny_filter, alpha_filter, shiny, alpha):
    if shiny_filter and not shiny:
        return False
    if alpha_filter and not alpha:
        return False
    
    return True

def check_common_spawn(index, distortion_name):
    return index not in [0,4,8,12,16,20] and distortion_name.lower() != "unknown"

def check_all_distortions(reader, map, rolls, shiny_filter, alpha_filter):
    return [check_distortion(reader, map, i, rolls, shiny_filter, alpha_filter) for i in range(num_distortions[map])]

def check_distortion(reader, map, index, rolls, shiny_filter, alpha_filter):
    print(f"Checking Group {index}")
    distortion_name = get_distortion_location(map, index)
    generator_seed = get_generator_seed(reader, map, index)
    group_id = (generator_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF

    group_seed, fixed_seed, encounter_slot, species, ec, pid, ivs, ability, gender, nature, shiny, alpha = \
            read_wild_rng(map, index, group_id, rolls)
    
    if group_seed == 0:
        return {
            "index": index,
            "spawn": False,
            "description": "Spawner not active",
        }
    
    else:
        if check_filter(shiny_filter, alpha_filter, shiny, alpha) and check_common_spawn(index, distortion_name):
            return  {
                "index": index,
                "spawn": True,
                "generator_seed": generator_seed,
                "distortion_name": distortion_name,
                "encounter_slot": encounter_slot,
                "species": species,
                "ec": ec,
                "pid": pid,
                "ivs": ivs,
                "ability": ability,
                "gender": gender,
                "nature": NATURES[nature],
                "shiny": shiny,
                "alpha": alpha,
            }
        else:
            return {
                "index": index,
                "spawn": False,
                "description": "Filtered"
            }