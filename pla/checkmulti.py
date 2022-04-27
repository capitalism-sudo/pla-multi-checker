import json

from .xoroshiro import XOROSHIRO

#with open("/home/cappy/pla-multi-checker-web/static/resources/text_natures.txt",encoding="utf-8") as text_natures:
with open("./static/resources/text_natures.txt",encoding="utf-8") as text_natures:
    NATURES = text_natures.read().split("\n")

#with open("/home/cappy/pla-multi-checker-web/static/resources/text_species_en.txt",encoding="utf-8") as text_species:
with open("./static/resources/text_species_en.txt",encoding="utf-8") as text_species:
    SPECIES = text_species.read().split("\n")

#RATIOS = json.load(open("/home/cappy/pla-multi-checker-web/static/resources/ratios.json"))
RATIOS = json.load(open("./static/resources/ratios.json"))

#encounter_table = json.load(open("/home/cappy/pla-multi-checker-web/static/resources/multi-es.json"))
encounter_table = json.load(open("./static/resources/multi-es.json"))

SPAWNER_PTR = "[[main+42a6ee0]+330]"

fixedgenders = ["Happiny", "Chansey", "Blissey", "Petilil", "Lilligant", "Bronzor", "Bronzong", "Voltorb", "Electrode", "Rotom", "Rufflet", "Braviary", "Unown"]


def generate_from_seed(seed,rolls,guaranteed_ivs=0,set_gender=False):
    rng = XOROSHIRO(seed)
    ec = rng.rand(0xFFFFFFFF)
    sidtid = rng.rand(0xFFFFFFFF)
    for _ in range(rolls):
        pid = rng.rand(0xFFFFFFFF)
        shiny = ((pid >> 16) ^ (sidtid >> 16) \
            ^ (pid & 0xFFFF) ^ (sidtid & 0xFFFF)) < 0x10
        if shiny:
            square = ((pid >> 16) ^ (sidtid >> 16) \
            ^ (pid & 0xFFFF) ^ (sidtid & 0xFFFF)) == 0x00
            break
        else:
            square = False
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
    return ec,pid,ivs,ability,gender,nature,shiny,square

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
        if species in fixedgenders:
            set_gender = True
        else:
            set_gender = False
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
        if species in fixedgenders:
            set_gender = True
        else:
            set_gender = False
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

    if isnight and encounter_table.get(f"{group_id}"+"n") is not None:
        print("Night check is ok")
        group_id = f"{group_id}" + "n"
        print(f"Group ID: {group_id}")
    
    display,_ = multi(group_seed,rolls,group_id,maxalive,maxdepth)

    for index in display:
        form = ''
        if " " in display[index]["species"] and "-" in display[index]["species"]:
            cutspecies = display[index]["species"].rpartition(' ')[2]
            form = display[index]["species"].rpartition('-')[2]
            cutspecies = cutspecies.rpartition('-')[0]     
        elif " " in display[index]["species"]:
            cutspecies = display[index]["species"].rpartition(' ')[2]
        elif "-" in display[index]["species"]:
            cutspecies = display[index]["species"].rpartition('-')[0]
            form = display[index]["species"].rpartition('-')[2]
        else:
            cutspecies = display[index]["species"]
        if display[index]["shiny"]:
            spritename = f"c_{SPECIES.index(cutspecies)}" \
                            f"{f'-{form}' if len(form) != 0 else ''}s.png"
        else:
            spritename = f"c_{SPECIES.index(cutspecies)}" \
                            f"{f'-{form}' if len(form) != 0 else ''}.png"
        display[index]["sprite"] = spritename
        ratioarray = RATIOS[str(SPECIES.index(cutspecies))]
        ratio = ratioarray[2]
        if display[index]["gender"] < ratio and cutspecies not in ["Bronzor", "Bronzong", "Rotom", "Voltorb", "Electrode", "Unown"]:
            display[index]["gender"] = "Female <i class='fa-solid fa-venus' style='color:pink'></i>"
        elif cutspecies in ["Bronzor", "Bronzong", "Rotom", "Voltorb", "Electrode","Unown"]:
            display[index]["gender"] = "Genderless <i class='fa-solid fa-genderless'></i>"
        else:
            display[index]["gender"] = "Male <i class='fa-solid fa-mars' style='color:blue'></i>"

    sorted_display = sorted(display.items(), key=lambda x: x[1]["adv"])
    sorted_dict = {}
    for key,value in enumerate(sorted_display):
        sorted_dict[key] = value[1]
        
    return sorted_dict