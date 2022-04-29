import json
from app import RESOURCE_PATH
from pla.core import generate_from_seed
from pla.core.util import get_sprite, get_gender_string
from pla.data import SPECIES, NATURES, is_fixed_gender, get_basespecies_form
from pla.rng import XOROSHIRO

encounter_table = json.load(open(RESOURCE_PATH + "/resources/multi-es.json"))

SPAWNER_PTR = "[[main+42a6ee0]+330]"

# Note - this function has undefinied variables - is it in use?
def read_mass_outbreak_rng(group_seed,rolls,remain):
    main_rng = XOROSHIRO(group_seed)
    for respawn in range(0,remain):
        generator_seed = respawn_rng.next()
        respawn_rng.next() # spawner 1's seed, unused
        respawn_rng = XOROSHIRO(respawn_rng.next())
        fixed_rng = XOROSHIRO(generator_seed)
        encounter_slot = (fixed_rng.next() / (2**64)) * encsum
        fixed_seed = fixed_rng.next()
        ec,pid,ivs,ability,gender,nature,shiny,square = generate_from_seed(fixed_seed,rolls)
        if shiny and encounter_slot > 122:
            print(f"{generator_seed:X} Advance {advance} Respawn {respawn} EC: {ec:08X} PID: {pid:08X} {'/'.join(str(iv) for iv in ivs)}")
            return True
    return False

def multi(group_seed,rolls,group_id,maxalive,maxdepth=5):
    path = []
    info = {}
    adv = 0
    curralive = maxalive

    group_seed = generate_initial_spawns(group_seed,rolls,group_id,maxalive,info)

    multi_recursion(info,path,group_seed,rolls,group_id,adv,maxdepth,maxalive,curralive)

    return info,path

def multi_recursion(info,path,group_seed,rolls,group_id,adv,maxdepth,maxalive,curralive):
    if adv > maxdepth:
        return

    if curralive > maxalive or curralive < 0:
        return

    curpath = path.copy()
    seed = group_seed

    for i in range(1,maxalive-curralive+1):
        curpath.append(i)
        seed = generate_spawns(group_seed,rolls,group_id,info,curpath,adv)
        if i != (maxalive-curralive):
            curpath.pop()

    if curralive == 0:
        curralive = maxalive

    adv += 1

    while curralive >= 0:
        curralive -= 1
        multi_recursion(info,curpath,seed,rolls,group_id,adv,maxdepth,maxalive,curralive)

def generate_spawns(group_seed,rolls,group_id,info,path,adv):
    #print(f"Seed: {group_seed}")
    main_rng = XOROSHIRO(group_seed)
    for i in range(path[len(path)-1]):
        gen_seed = main_rng.next()
        main_rng.next()
        fixed_rng = XOROSHIRO(gen_seed)
        encsum = get_encounter_slot_sum(group_id)
        encounter_slot = (fixed_rng.next()/(2**64)) * encsum
        fixed_seed = fixed_rng.next()
        species,alpha = get_species(encounter_slot,group_id)
        set_gender = is_fixed_gender(species) or species == "Basculin-2"
        guaranteed_ivs = 3 if alpha else 0
        ec,pid,ivs,ability,gender,nature,shiny,square = \
            generate_from_seed(fixed_seed,rolls,guaranteed_ivs,set_gender)
        currpath = f"{path[:len(path)-1] + [i+1]}"
        poke = {
            "spawn":True,
            "ec":f"{ec:X}",
            "pid":f"{pid:X}",
            "ivs":ivs,
            "ability":ability,
            "gender":gender,
            "nature": NATURES[nature],
            "shiny":shiny,
            "square":square,
            "species":species,
            "alpha":alpha,
            "path":(path[:len(path)-1] + [i+1]),
            "adv":adv
        }
        info[str(currpath)] = poke
    group_seed = main_rng.next()
    #print(f"Finished Seed: {group_seed}")
    return group_seed

def generate_initial_spawns(group_seed,rolls,group_id,maxalive,info):
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
        species,alpha = get_species(encounter_slot,group_id)
        set_gender = is_fixed_gender(species) or species == "Basculin-2"
        guaranteed_ivs = 3 if alpha else 0
        ec,pid,ivs,ability,gender,nature,shiny,square = \
            generate_from_seed(fixed_seed,rolls,guaranteed_ivs,set_gender)
        poke = {
            "spawn":True,
            "ec":f"{ec:X}",
            "pid":f"{pid:X}",
            "ivs":ivs,
            "ability":ability,
            "gender":gender,
            "nature": NATURES[nature],
            "shiny":shiny,
            "square":square,
            "species":species,
            "alpha":alpha,
            "path":f"Initial {i}",
            "adv":0
        }
        currpath = f"Initial {i}"
        info[str(currpath)] = poke
    group_seed = main_rng.next()
    #print(f"Finished Seed: {group_seed}")
    return group_seed

def get_species(encounter_slot,group_id):
    encsum = 0
    for slot in encounter_table[str(group_id)]:
        encsum += slot["slot"]
        if encounter_slot < encsum:
            return slot["species"],slot["alpha"]

def get_encounter_slot_sum(group_id):
    encsum = 0
    for slot in encounter_table[str(group_id)]:
        encsum += slot["slot"]

    return encsum

def check_multi_spawner(reader,rolls,group_id,maxalive,maxdepth,isnight):
    generator_seed = reader.read_pointer_int(f"{SPAWNER_PTR}"\
                                             f"+{0x70+group_id*0x440+0x20:X}",8)
    group_seed = (generator_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF

    print(f"Spawner Pointer: {SPAWNER_PTR}+{0x70+group_id*0x440+0x20:X}")

    return check_multi_spawner_seed(group_seed,rolls,group_id,maxalive,maxdepth,isnight)

def check_multi_spawner_seed(group_seed,rolls,group_id,maxalive,maxdepth,isnight):
    if isnight and encounter_table.get(f"{group_id}"+"n") is not None:
        print("Night check is ok")
        group_id = f"{group_id}" + "n"
        print(f"Group ID: {group_id}")
    
    group_seed = int(group_seed)
    
    display,_ = multi(group_seed,rolls,group_id,maxalive,maxdepth)

    for index in display:
        cutspecies, form = get_basespecies_form(display[index]["species"])
        display[index]["sprite"] = get_sprite(cutspecies, form, display[index]["shiny"])
        display[index]["gender"] = get_gender_string(cutspecies, display[index]["gender"])

    sorted_display = sorted(display.items(), key=lambda x: x[1]["adv"])
    sorted_dict = {}
    for key,value in enumerate(sorted_display):
        sorted_dict[key] = value[1]
        
    return sorted_dict
