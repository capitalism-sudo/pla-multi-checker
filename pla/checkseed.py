# Go to root of PyNXReader
import json
import struct
import random
from datetime import datetime

from .xoroshiro import XOROSHIRO


mapnamevals = {
    "5504":"Crimson Mirelands",
    "5351":"Alabaster Icelands",
    "519E":"Coronet Highlands",
    "5A1D":"Obsidian Fieldlands",
    "56B7":"Cobalt Coastlands"}

encmap = json.load(open("./static/resources/mmo_es.json"))

allpaths = json.load(open("./static/resources/mmopaths.json"))

nonbonuspaths = json.load(open("./static/resources/nonbonuspaths.json"))

with open("./static/resources/text_natures.txt",encoding="utf-8") as text_natures:
    NATURES = text_natures.read().split("\n")

with open("./static/resources/text_species_en.txt",encoding="utf-8") as text_species:
    SPECIES = text_species.read().split("\n")

RATIOS = json.load(open("./static/resources/ratios.json"))

extrapaths = [[],[1],[2],[2,1],[3],[3,1],[3,2],[3,2,1]]
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


def generate_mass_outbreak_aggressive_path(group_seed,rolls,paths,spawns,true_spawns,
                                           encounters,encsum,isbonus=False,isalpha=False):
    """Generate all the pokemon of an outbreak based on a provided aggressive path"""
    # pylint: disable=too-many-locals, too-many-arguments
    # the generation is unique to each path, no use in splitting this function
    storage = {}
    uniques = set()
    true_seed = int(group_seed)
    for i, steps in enumerate(paths):
        main_rng = XOROSHIRO(true_seed)
        for init_spawn in range(1,5):
            generator_seed = main_rng.next()
            main_rng.next() # spawner 1's seed, unused
            fixed_rng = XOROSHIRO(generator_seed)
            encounter_slot = (fixed_rng.next() / (2**64)) * encsum
            species,alpha,nomodspecies = get_species(encounters,encounter_slot)
            if nomodspecies in fixedgenders:
                set_gender = True
            else:
                set_gender = False
            if isbonus and alpha:
                guaranteed_ivs = 4
            elif isbonus or alpha:
                guaranteed_ivs = 3
            else:
                guaranteed_ivs = 0
            fixed_seed = fixed_rng.next()
            encryption_constant,pid,ivs,ability,gender,nature,shiny = \
                generate_from_seed(fixed_seed,rolls,guaranteed_ivs,set_gender)
            if not fixed_seed in uniques:
                uniques.add(fixed_seed)
                info = {
                    "index":f"<span class='pla-results-init'>Init Spawn " \
                    f"{init_spawn} </span></span>",
                    "spawn":True,
                    "generator_seed":f"{generator_seed:X}",
                    "species":species,
                    "shiny":shiny,
                    "alpha":alpha,
                    "ec":encryption_constant,
                    "pid":pid,
                    "ivs":ivs,
                    "ability":ability,
                    "nature":NATURES[nature],
                    "gender":gender
                    }
                """
                if not fixed_seed in uniques:
                    info["unique"] = True
                    uniques.add(fixed_seed)
                else:
                    info["unique"] = False
                """
                if not isbonus:
                    info["defaultroute"] = True
                else:
                    info["defaultroute"] = False
                #print(info)
                storage[f"{fixed_seed} + {init_spawn} + " \
                        f"{random.randint(0,100)} + {i} + {steps}"]=info
        group_seed = main_rng.next()
        respawn_rng = XOROSHIRO(group_seed)
        for step_i,step in enumerate(steps):
            for pokemon in range(1,step+1):
                generator_seed = respawn_rng.next()
                respawn_rng.next() # spawner 1's seed, unused
                fixed_rng = XOROSHIRO(generator_seed)
                encounter_slot = (fixed_rng.next() / (2**64)) * encsum
                species,alpha,nomodspecies = get_species(encounters,encounter_slot)
                if nomodspecies in fixedgenders:
                    set_gender = True
                else:
                    set_gender = False
                if isbonus and alpha:
                    guaranteed_ivs = 4
                elif isbonus or alpha:
                    guaranteed_ivs = 3
                else:
                    guaranteed_ivs = 0
                fixed_seed = fixed_rng.next()
                encryption_constant,pid,ivs,ability,gender,nature,shiny = \
                    generate_from_seed(fixed_seed,rolls,guaranteed_ivs,set_gender)
                if not fixed_seed in uniques and (sum(steps[:step_i]) + pokemon + 4) <= true_spawns:
                    uniques.add(fixed_seed)
                    info = {
                    "index":f"Path: {'|'.join(str(s) for s in steps[:step_i] + [pokemon])} </span>",
                    "spawn":True,
                    "generator_seed":f"{generator_seed:X}",
                    "species":species,
                    "shiny":shiny,
                    "alpha":alpha,
                    "ec":encryption_constant,
                    "pid":pid,
                    "ivs":ivs,
                    "ability":ability,
                    "nature":NATURES[nature],
                    "gender":gender
                    }
                    """
                    if not fixed_seed in uniques:
                        uniques.add(fixed_seed)
                        info["unique"] = True
                    else:
                        info["unique"] = False
                    """
                    if not isbonus and sum(steps[:step_i]) == len(steps[:step_i]) and pokemon == 1:
                        info["defaultroute"] = True
                    else:
                        info["defaultroute"] = False
                   # print(info)
                    storage[f"{fixed_seed} + {steps[:step_i] + [pokemon]} " \
                            f"+ {random.randint(0,100)} + {i} + {steps}"]=info
            respawn_rng = XOROSHIRO(respawn_rng.next())
    return storage

def get_bonus_seed(group_seed,rolls,path,max_spawns):
    main_rng = XOROSHIRO(int(group_seed))
    for init_spawn in range(4):
        generator_seed = main_rng.next()
        main_rng.next() # spawner 1's seed, unused
    group_seed = main_rng.next()
    main_rng = XOROSHIRO(group_seed)
    respawn_rng = XOROSHIRO(group_seed)
    generator_seed = 0
    for respawn,step in enumerate(path):
        for pokemon in range(0,step):
            generator_seed = respawn_rng.next()
            tempseed = respawn_rng.next() # spawner 1's seed, unused
        respawn_rng = XOROSHIRO(respawn_rng.next())
    bonus_seed = (respawn_rng.next() - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF
    return bonus_seed

def read_mass_outbreak_rng(rolls,group_seed,max_spawns,encounter,bonus_flag):
    print(f"Species Group: FUCKING BULBASAUR")
    encounters = {}
    encounters,encsum = get_encounter_table(encounter)
    paths = nonbonuspaths[str(max_spawns)]

    true_spawns = max_spawns
    if bonus_flag:
        max_spawns = 10
    else:
        max_spawns += 3
    display = generate_mass_outbreak_aggressive_path(group_seed,rolls,paths,max_spawns,
                                                     true_spawns,encounters,encsum,bonus_flag,False)
    return display

def get_encounter_table(encounter):
    encounters = {}
    encsum = 0
    """
    if bonus:
        enc_pointer = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                              f"{0x1d4+group_id*0x90 + 0xb80 * mapcount+0x2c:X}",8)
    else:
        enc_pointer = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                              f"{0x1d4+group_id*0x90 + 0xb80 * mapcount+0x24:X}",8)
    """

    #enc_pointer = f"{enc_pointer:X}"
    """
    if bonus:
        enc_pointer = "44182B854CD3745D"
    else:
        enc_pointer = "7FA3A1DE69BD271E"
    """
    enc_pointer = encounter
    #enc_pointer = enc_pointer.upper()
    #enc_pointer = "0x"+enc_pointer

    if enc_pointer not in encmap.keys():
        #print(f"Enc pointer not found in encmap")
        return None,0
    else:
        encounters = encmap[enc_pointer]

    #Get encounter table sum
    for species in encounters:
        encsum += species['slot']

    return encounters,encsum

def get_species(encounters,encounter_slot):
    alpha = False
    encsum = 0


    for species in encounters:
        encsum += species['slot']
        if encounter_slot < encsum:
            alpha = species['alpha']
            slot = species['name']
            nomodslot = slot
            if alpha:
                slot = "Alpha "+slot
            return slot,alpha,nomodslot

    return "",False

def get_gen_seed_to_group_seed(reader,group_id):

    gen_seed = reader.read_pointer_int(f"[[[[[[main+42EEEE8]+78]+" \
                                       f"{0xD48 + group_id*0x8:X}]+58]+38]+478]+20",8)
    group_seed = (gen_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF

    return group_seed

def generate_mass_outbreak_aggressive_path_normal(group_seed,rolls,steps,uniques,storage):
    """Generate all the pokemon of an outbreak based on a provided aggressive path"""
    # pylint: disable=too-many-locals, too-many-arguments
    # the generation is unique to each path, no use in splitting this function
    main_rng = XOROSHIRO(group_seed)
    for init_spawn in range(1,5):
        generator_seed = main_rng.next()
        main_rng.next() # spawner 1's seed, unused
        fixed_rng = XOROSHIRO(generator_seed)
        slot = (fixed_rng.next() / (2**64) * 101)
        alpha = slot >= 100
        fixed_seed = fixed_rng.next()
        encryption_constant,pid,ivs,ability,gender,nature,shiny = \
            generate_from_seed(fixed_seed,rolls,3 if alpha else 0)
        if not fixed_seed in uniques:
            uniques.add(fixed_seed)
            info = {
                "index":f"Init Spawn {init_spawn}</span>",
                "spawn":True,
                "generator_seed":f"{generator_seed:X}",
                "shiny":shiny,
                "alpha":alpha,
                "ec":encryption_constant,
                "pid":pid,
                "ivs":ivs,
                "ability":ability,
                "nature":NATURES[nature],
                "gender":gender,
                "defaultroute": True
                }
            #print(info)
            storage[str(fixed_seed)]=info
    group_seed = main_rng.next()
    respawn_rng = XOROSHIRO(group_seed)
    for step_i,step in enumerate(steps):
        for pokemon in range(1,step+1):
            generator_seed = respawn_rng.next()
            respawn_rng.next() # spawner 1's seed, unused
            fixed_rng = XOROSHIRO(generator_seed)
            slot = (fixed_rng.next() / (2**64) * 101)
            alpha = slot >= 100
            fixed_seed = fixed_rng.next()
            encryption_constant,pid,ivs,ability,gender,nature,shiny = \
                generate_from_seed(fixed_seed,rolls,3 if alpha else 0)
            if not fixed_seed in uniques:
                uniques.add(fixed_seed)
                info = {
                "index":f"Path: {'|'.join(str(s) for s in steps[:step_i] + [pokemon])}</span>",
                "spawn":True,
                "generator_seed":f"{generator_seed:X}",
                "shiny":shiny,
                "alpha":alpha,
                "ec":encryption_constant,
                "pid":pid,
                "ivs":ivs,
                "ability":ability,
                "nature":NATURES[nature],
                "gender":gender
                }
                if len(steps[:step_i]) == sum(steps[:step_i]) and pokemon == 1:
                    info["defaultroute"] = True
                else:
                    info["defaultroute"] = False
               # print(info)
                storage[str(fixed_seed)]=info
        respawn_rng = XOROSHIRO(respawn_rng.next())

def get_final_normal(spawns):
    """Get the final path that will be generated to know when to stop aggressive recursion"""
    spawns -= 4
    path = [4] * (spawns // 4)
    if spawns % 4 != 0:
        path.append(spawns % 4)
    return path


def aggressive_outbreak_pathfind_normal(group_seed,
                                 rolls,
                                 spawns,
                                 step=0,
                                 steps=None,
                                 uniques=None,
                                 storage=None):
    """Recursively pathfind to possible shinies for the current outbreak via multi battles"""
    # pylint: disable=too-many-arguments
    # can this algo be improved?
    if steps is None or uniques is None or storage is None:
        steps = []
        uniques = set()
        storage = {}
    _steps = steps.copy()
    if step != 0:
        _steps.append(step)
    if sum(_steps) + step < spawns - 4:
        for _step in range(1, min(5, (spawns - 4) - sum(_steps))):
            if aggressive_outbreak_pathfind_normal(group_seed,
                                            rolls,
                                            spawns,
                                            _step,
                                            _steps,
                                            uniques,
                                            storage) is not None:
                return storage
    else:
        _steps.append(spawns - sum(_steps) - 4)
        generate_mass_outbreak_aggressive_path_normal(group_seed,rolls,_steps,uniques,storage)
        if _steps == get_final_normal(spawns):
            return storage
    return None

def next_filtered_aggressive_outbreak_pathfind_normal(group_seed,rolls,spawns):
    """Check the next outbreak advances until an aggressive path to a pokemon that
       passes poke_filter exists"""
    main_rng = XOROSHIRO(group_seed)
    result = []
    advance = -1

    while len(result) == 0 and advance < 1:
        if advance != -1:
            for _ in range(4*2):
                main_rng.next()
            group_seed = main_rng.next()
            main_rng.reseed(group_seed)
        advance += 1
        result = aggressive_outbreak_pathfind_normal(group_seed, rolls, spawns)
        if result is None:
            result = []
    if advance == 0:
        info = result
    else:
        info = {
            "spawn":False,
            "description":"Spawner not active"
            }
    if advance != 0:
        return info
    else:
        return info

def get_group_seed(reader,group_id,mapcount):
    group_seed = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                         f"{0x1d4+group_id*0x90 + 0xb80 * mapcount+0x44:X}",8)
    return group_seed

def get_max_spawns(reader,group_id,maps,isbonus):
    if isbonus:
        max_spawns = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                             f"{0x1d4+group_id*0x90 + 0xb80 * maps+0x60:X}",4)
    else:
        max_spawns = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                             f"{0x1d4+group_id*0x90 + 0xb80 * maps+0x4c:X}",4)

    return max_spawns

def get_map_name(reader,maps):

    mapname = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                      f"{0x1d4 + 0xb80 * maps - 0x24:X}",2)
    mapname = f"{mapname:X}"
    mapname = mapnamevals.get(mapname, "None")

    return mapname

def get_bonus_flag(reader,group_id,maps):

    return True if reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                           f"{0x1d4+group_id*0x90 + 0xb80 * maps+0x18:X}"
                                           ,1) == 1 else False


def get_normal_outbreak_info(reader,group_id,inmap):
    species = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                      f"{0x20 + group_id*0x50:X}",2)
    if not inmap:
        group_seed = get_group_seed(reader,group_id,0)
    else:
        group_seed = get_gen_seed_to_group_seed(reader,group_id)

    max_spawns = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                         f"{0x20 + group_id*0x50+0x40:X}",8)

    coords = struct.unpack('fff',reader.read_pointer(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                                     f"{0x20 + group_id*0x50+0x20:X}",12))

    coordinates = {
        "x":coords[0],
        "y":coords[1],
        "z":coords[2]
    }

    return species,group_seed,max_spawns,coordinates

def read_bonus_pathinfo(paths,rolls,group_seed,map_name,
                        true_spawns,bonus_spawns,max_spawns,encounter):
    #pylint: disable=too-many-branches
    """reads info about a bonus path"""
    isbonus = True
    outbreaks = {}
    nbpaths = nonbonuspaths[str(true_spawns)]
    for tex,value in enumerate(paths):
        seed = get_bonus_seed(group_seed,rolls,value,max_spawns)
        extra = [1] * (max_spawns - sum(value))
        encounters,encsum = get_encounter_table(encounter)
        for ext,epath in enumerate(extrapaths):
            spawn_remain = max_spawns - sum(value)
            if epath == []:
                display = generate_mass_outbreak_aggressive_path(seed,rolls,nbpaths,
                                                                 bonus_spawns,
                                                                 true_spawns,encounters,
                                                                 encsum,isbonus,False)
            elif epath[0] < spawn_remain:
                epath_seed = get_extra_path_seed(seed,epath)
                display = generate_mass_outbreak_aggressive_path(epath_seed,rolls,
                                                                 nbpaths,bonus_spawns,true_spawns,
                                                                 encounters,encsum,isbonus,False)
            else:
                continue
            for index in display:
                form = ''
                if epath == []:
                    display[index]["index"] = f"<span class='pla-results-firstpath'>" \
                                              f"First Round Path: " \
                                              f"{value} </span> + {extra} + " \
                                              f"<span class='pla-results-bonus'> Bonus Round Path" \
                                              + display[index]["index"]
                else:
                    display[index]["index"] = f"<span class='pla-results-firstpath'>First Round Path: " \
                                              f"{value} </span> + <span class='pla-results-revisit'> " \
                                              f"Revisit {epath} </span> + <span class='pla-results-bonus'> " \
                                              f"Bonus Round Path " \
                                              + display[index]["index"]
                display[index]["group"] = 0
                display[index]["mapname"] = map_name
                display[index]["numspawns"] = max_spawns
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
                if display[index]["gender"] <= ratio and cutspecies not in ["Bronzor", "Bronzong", "Rotom", "Voltorb", "Electrode", "Unown"]:
                    display[index]["gender"] = "Female <i class='fa-solid fa-venus' style='color:pink'></i>"
                elif cutspecies in ["Bronzor", "Bronzong", "Rotom", "Voltorb", "Electrode","Unown"]:
                    display[index]["gender"] = "Genderless <i class='fa-solid fa-genderless'></i>"
                else:
                    display[index]["gender"] = "Male <i class='fa-solid fa-mars' style='color:blue'></i>"
                if len(value) == sum(value):
                    display[index]["defaultroute"] = True
                else:
                    display[index]["defaultroute"] = False

            outbreaks["Bonus" + f"{tex} {value}" + f" {ext} {epath}"] = display

    return outbreaks
                                         
def check_from_seed(group_seed,rolls,frencounter,brencounter,bonus_flag=False,max_spawns=10,br_spawns=7):
    #pylint: disable=too-many-branches,too-many-locals,too-many-arguments
    """reads a single map's MMOs"""
    print(RATIOS)
    if len(frencounter) == 0:
        frencounter = "7FA3A1DE69BD271E"
    if len(brencounter) == 0:
        brencounter = "441828854CD36F44"
    i = 0
    outbreaks = {}
    print(f"Rolls: {rolls}")
    map_name = "DOES NOT MATTER"
    #enctable,_ = get_encounter_table(reader,i,mapcount,True)
    #bonus_flag = False if enctable is None else True
    #bonus_flag = True
    numspecies = 1
    #max_spawns = 10
    display = read_mass_outbreak_rng(rolls,group_seed,max_spawns,frencounter,False)
    for index in display:
        if index not in ('index','description'):
            form = ''
            display[str(index)]["group"] = 0
            display[str(index)]["mapname"] = map_name
            display[str(index)]["numspawns"] = max_spawns
            if " " in display[str(index)]["species"] and "-" in display[str(index)]["species"]:
                cutspecies = display[str(index)]["species"].rpartition(' ')[2]
                form = display[str(index)]["species"].rpartition('-')[2]
                cutspecies = cutspecies.rpartition('-')[0]     
            elif " " in display[str(index)]["species"]:
                cutspecies = display[str(index)]["species"].rpartition(' ')[2]
            elif "-" in display[str(index)]["species"]:
                cutspecies = display[str(index)]["species"].rpartition('-')[0]
                form = display[str(index)]["species"].rpartition('-')[2]
            else:
                cutspecies = display[str(index)]["species"]
            if display[str(index)]["shiny"]:
                spritename = f"c_{SPECIES.index(cutspecies)}{f'-{form}' if len(form) != 0 else ''}s.png"
            else:
                spritename = f"c_{SPECIES.index(cutspecies)}{f'-{form}' if len(form) != 0 else ''}.png"
            display[str(index)]["sprite"] = spritename
            ratioarray = RATIOS[str(SPECIES.index(cutspecies))]
            ratio = ratioarray[2]
            #print(f"Ratio: {ratio}")
            if display[str(index)]["gender"] <= ratio and cutspecies not in ["Bronzor", "Bronzong", "Rotom", "Voltorb", "Electrode", "Unown"]:
                display[str(index)]["gender"] = "Female <i class='fa-solid fa-venus' style='color:pink'></i>"
            elif cutspecies in ["Bronzor", "Bronzong", "Rotom", "Voltorb", "Electrode","Unown"]:
                display[str(index)]["gender"] = "Genderless <i class='fa-solid fa-genderless'></i>"
            else:
                display[str(index)]["gender"] = "Male <i class='fa-solid fa-mars' style='color:blue'></i>"
    if bonus_flag:
        true_spawns = max_spawns
        bonus_spawns = true_spawns + 4
        bonus_seed = allpaths[str(max_spawns)]
        true_spawns = br_spawns
        result = read_bonus_pathinfo(bonus_seed,rolls,group_seed,map_name,true_spawns,bonus_spawns,max_spawns,brencounter)
        print(f"Group {i} Bonus Complete!")
    outbreaks[f"{i} " + f"{bonus_flag}"] = display
    print(f"Group {i} Complete!")
    if bonus_flag:
        outbreaks[f"{i} " + f"{bonus_flag}" + "bonus"] = result

    return outbreaks

def get_all_map_mmos(reader,rolls,inmap):
    """reads all mmos on the map"""
    display = {}
    starttime = datetime.now()
    print(f"Starting at {starttime}")
    for i in range(0,4):
        map_name = get_map_name(reader,i)
        if map_name == "None":
            continue
        print(f"Map {map_name} starting now...")
        result = get_map_mmos(reader,i,rolls,inmap)
        display[map_name] = result
        print(f"Map {map_name} complete!")

    endtime = datetime.now()
    print(f"Task done at {endtime}, Took {endtime - starttime}")
    print(len(display))
    return display


def get_all_map_names(reader):
    """gets all map names"""
    maps = []
    for i in range(0,4):
        map_name = get_map_name(reader,i)
        maps.append(map_name)

    return maps

def read_normal_outbreaks(reader,rolls,inmap):
    """reads all normal outbreaks on map"""
    outbreaks = {}
    rolls = rolls + 13
    print(f"Rolls: {rolls}")
    for i in range(0,4):
        species,group_seed,max_spawns,coordinates = get_normal_outbreak_info(reader,i,inmap)
        if species != 0:
            display = next_filtered_aggressive_outbreak_pathfind_normal(group_seed,rolls,max_spawns)
            for index in display:
                if index not in ('index', 'description'):
                    form = ''
                    display[str(index)]["group"] = i
                    display[str(index)]["mapname"] = "Normal Outbreak"
                    display[str(index)]["numspawns"] = max_spawns
                    if SPECIES[species] == "Basculin":
                        display[str(index)]["species"] = "Basculin-2"
                    else:
                        display[str(index)]["species"] = SPECIES[species]
                    display[str(index)]["coords"] = coordinates
                    if " " in display[str(index)]["species"] and "-" in display[str(index)]["species"]:
                        cutspecies = display[str(index)]["species"].rpartition(' ')[2]
                        form = display[str(index)]["species"].rpartition('-')[2]
                        cutspecies = cutspecies.rpartition('-')[0]     
                    elif " " in display[str(index)]["species"]:
                        cutspecies = display[str(index)]["species"].rpartition(' ')[2]
                    elif "-" in display[str(index)]["species"]:
                        cutspecies = display[str(index)]["species"].rpartition('-')[0]
                        form = display[str(index)]["species"].rpartition('-')[2]
                    else:
                        cutspecies = display[str(index)]["species"]
                    if display[str(index)]["shiny"]:
                        spritename = f"c_{SPECIES.index(cutspecies)}{f'-{form}' if len(form) != 0 else ''}s.png"
                    else:
                        spritename = f"c_{SPECIES.index(cutspecies)}{f'-{form}' if len(form) != 0 else ''}.png"
                    display[str(index)]["sprite"] = spritename
            outbreaks[f"Outbreak {i}"] = display

    return outbreaks


def get_all_outbreak_names(reader,inmap):
    """gets all map names of outbreak locations"""
    outbreaks = []
    for i in range(0,4):
        species,_,_,_ = get_normal_outbreak_info(reader,i,inmap)
        if species != 0:
            outbreaks.append(SPECIES[species])

    return outbreaks

def read_group_coordinates(reader,group_id,mapcount):
    """reads coordinates of mmo group"""
    coords = struct.unpack('fff',reader.read_pointer(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                                     f"{0x1d4+group_id*0x90 + 0xb80 * mapcount - 0x14:X}",12))
    coordinates = {
        "x":coords[0],
        "y":coords[1],
        "z":coords[2]
        }
    return coordinates

def teleport_to_spawn(reader,coords):
    """Teleports user to spawn point"""
    cordarray = []
    playerloc = "[[[[[[main+42D4720]+18]+48]+1F0]+18]+370]+90"
    for i in coords:
        cordarray.append(coords[i])

    print(f"Teleporting to {cordarray}")
    position_bytes = struct.pack('fff', *cordarray)
    reader.write_pointer(playerloc,f"{int.from_bytes(position_bytes,'big'):024X}")


def get_extra_path_seed(group_seed,path):
    """Gets the seed for an extra path"""
    respawn_rng = XOROSHIRO(group_seed)
    for _,step in enumerate(path):
        for _ in range(0,(4 -step)):
            respawn_rng.next()
            respawn_rng.next() # spawner 1's seed, unused
        respawn_rng = XOROSHIRO(respawn_rng.next())
    bonus_seed = (respawn_rng.next() - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF
    return bonus_seed
