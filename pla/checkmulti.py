import json
from app import RESOURCE_PATH
from pla.core import BASE_ROLLS, generate_from_seed, get_rolls, get_sprite
from pla.data import pokedex, natures
from pla.rng import XOROSHIRO

encounter_table = json.load(open(RESOURCE_PATH + "resources/multi-es.json"))

SPAWNER_PTR = "[[main+42a6ee0]+330]"

def multi(group_seed, research, group_id, maxalive, maxdepth=5, rolls_override=None):
    path = []
    info = {}
    adv = 0
    curralive = maxalive

    group_seed = generate_initial_spawns(group_seed, research, group_id, maxalive, info, rolls_override)

    multi_recursion(info,path,group_seed,research,group_id,adv,maxdepth,maxalive,curralive,rolls_override)

    return info,path

def multi_recursion(info,path,group_seed,research,group_id,adv,maxdepth,maxalive,curralive,rolls_override=None):
    if adv > maxdepth:
        return

    if curralive > maxalive or curralive < 0:
        return

    curpath = path.copy()
    seed = group_seed

    for i in range(1, maxalive-curralive+1):
        curpath.append(i)
        seed = generate_spawns(group_seed, research, group_id, info, curpath, adv, rolls_override)
        if i != (maxalive-curralive):
            curpath.pop()

    if curralive == 0:
        curralive = maxalive

    adv += 1

    while curralive >= 0:
        curralive -= 1
        multi_recursion(info,curpath,seed,research,group_id,adv,maxdepth,maxalive,curralive,rolls_override)

def generate_spawns(group_seed, research, group_id, info, path, adv, rolls_override = None):
    #print(f"Seed: {group_seed}")
    main_rng = XOROSHIRO(group_seed)
    for i in range(path[-1]):
        gen_seed = main_rng.next()
        main_rng.next()
        fixed_rng = XOROSHIRO(gen_seed)
        encsum = get_encounter_slot_sum(group_id)
        encounter_slot = (fixed_rng.next()/(2**64)) * encsum
        fixed_seed = fixed_rng.next()
        pokemon, alpha = get_species(encounter_slot, group_id)

        # Account for the Basculin-specific mechanics
        set_gender = pokemon.is_fixed_gender() or pokemon.id == "Basculin-2"

        guaranteed_ivs = 3 if alpha else 0
        rolls = rolls_override if rolls_override is not None else get_rolls(pokemon, research, BASE_ROLLS)
        ec,pid,ivs,ability,gender,nature,shiny,square = \
            generate_from_seed(fixed_seed,rolls,guaranteed_ivs,set_gender)
        gender = pokemon.calculate_gender(gender)
        
        currpath = f"{path[:len(path)-1] + [i+1]}"
        info[currpath] = {
            "ec": ec,
            "pid": pid,
            "ivs": ivs,
            "ability": ability,
            "gender": gender.value,
            "nature": natures(nature),
            "shiny": shiny,
            "square": square,
            "species": pokemon.display_name(),
            "sprite": get_sprite(pokemon, shiny, gender),
            "alpha": alpha,
            "rolls": rolls,
            "path": (path[:len(path)-1] + [i+1]),
            "adv": adv
        }
    
    group_seed = main_rng.next()
    #print(f"Finished Seed: {group_seed}")
    return group_seed

def generate_initial_spawns(group_seed, research, group_id, maxalive, info, rolls_override = None):
    #print(f"Seed: {group_seed}")
    main_rng = XOROSHIRO(group_seed)
    for i in range(1,maxalive+1):
    #for i in range(1,3):
        gen_seed = main_rng.next()
        main_rng.next()
        fixed_rng = XOROSHIRO(gen_seed)
        encsum = get_encounter_slot_sum(group_id)
        encounter_slot = (fixed_rng.next()/(2**64)) * encsum
        fixed_seed = fixed_rng.next()
        pokemon, alpha = get_species(encounter_slot, group_id)

        # Account for the Basculin-specific mechanics
        set_gender = pokemon.is_fixed_gender() or pokemon.id == "Basculin-2"

        guaranteed_ivs = 3 if alpha else 0
        rolls = rolls_override if rolls_override is not None else get_rolls(pokemon, research, BASE_ROLLS)
        ec,pid,ivs,ability,gender,nature,shiny,square = \
            generate_from_seed(fixed_seed,rolls,guaranteed_ivs,set_gender)
        gender = pokemon.calculate_gender(gender)
        
        currpath = f"Initial {i}"
        info[currpath] = {
            "ec": ec,
            "pid": pid,
            "ivs": ivs,
            "ability": ability,
            "gender": gender.value,
            "nature": natures(nature),
            "shiny": shiny,
            "square": square,
            "species": pokemon.display_name(),
            "sprite": get_sprite(pokemon, shiny, gender),
            "alpha": alpha,
            "rolls": rolls,
            "path": f"Initial {i}",
            "adv": 0
        }
    
    group_seed = main_rng.next()
    #print(f"Finished Seed: {group_seed}")
    return group_seed

def get_species(encounter_slot, group_id):
    encsum = 0
    for slot in encounter_table[str(group_id)]:
        encsum += slot["slot"]
        if encounter_slot < encsum:
            return pokedex.entry(slot['species']), slot['alpha']

def get_encounter_slot_sum(group_id):
    return sum(e['slot'] for e in encounter_table[str(group_id)])

def check_multi_spawner(reader, research, group_id, maxalive, maxdepth, isnight, rolls_override = None):
    generator_seed = reader.read_pointer_int(f"{SPAWNER_PTR}"\
                                             f"+{0x70 + group_id*0x440 + 0x20:X}",8)
    group_seed = (generator_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF

    print(f"Spawner Pointer: {SPAWNER_PTR}+{0x70 + group_id*0x440 + 0x20:X}")

    return check_multi_spawner_seed(group_seed,research,group_id,maxalive,maxdepth,isnight,rolls_override)

def check_multi_spawner_seed(group_seed, research, group_id, maxalive, maxdepth, isnight, rolls_override = None):
    if isnight and encounter_table.get(f"{group_id}"+"n") is not None:
        print("Night check is ok")
        group_id = f"{group_id}" + "n"
        print(f"Group ID: {group_id}")
    
    display,_ = multi(group_seed, research, group_id, maxalive, maxdepth, rolls_override)

    sorted_display = sorted(display.items(), key=lambda x: x[1]["adv"])
    sorted_dict = {}
    for key,value in enumerate(sorted_display):
        sorted_dict[key] = value[1]
        
    return sorted_dict
