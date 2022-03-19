# Go to root of PyNXReader
import sys
import json
import struct
from datetime import datetime

from .xoroshiro import XOROSHIRO


mapnamevals = {
    "5504":"Crimson Mirelands",
    "5351":"Alabaster Icelands",
    "519E":"Coronet Highlands",
    "5A1D":"Obsidian Fieldlands",
    "56B7":"Cobalt Coastlands"}

encmap = json.load(open("./static/resources/mmo_es.json"))

with open("./static/resources/text_natures.txt",encoding="utf-8") as text_natures:
    NATURES = text_natures.read().split("\n")

with open("./static/resources/text_species_en.txt",encoding="utf-8") as text_species:
    SPECIES = text_species.read().split("\n")

extrapaths = [[],[1],[2],[2,1],[3],[3,1],[3,2],[3,2,1]]
    
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


def generate_mass_outbreak_aggressive_path(group_seed,rolls,steps,uniques,storage,spawns,true_spawns,encounters,encsum,isbonus=False,isalpha=False):
    """Generate all the pokemon of an outbreak based on a provided aggressive path"""
    # pylint: disable=too-many-locals, too-many-arguments
    # the generation is unique to each path, no use in splitting this function
    main_rng = XOROSHIRO(group_seed)
    for init_spawn in range(1,5):
        generator_seed = main_rng.next()
        main_rng.next() # spawner 1's seed, unused
        fixed_rng = XOROSHIRO(generator_seed)
        encounter_slot = (fixed_rng.next() / (2**64)) * encsum
        species,alpha = get_species(encounters,encounter_slot)
        if isbonus and alpha:
            guaranteed_ivs = 4
        elif isbonus or alpha:
            guaranteed_ivs = 3
        else:
            guaranteed_ivs = 0
        fixed_seed = fixed_rng.next()
        encryption_constant,pid,ivs,ability,gender,nature,shiny = \
            generate_from_seed(fixed_seed,rolls,guaranteed_ivs)
        #print(f"Species: {noformspecies} alphafilter: {alphafilter} shinyfilter: {shinyfilter} blacklistfilter: {blacklistfilter} whitelistfilter: {whitelistfilter} alpha: {alpha}")
        if not fixed_seed in uniques:
        #if not fixed_seed in uniques and isbonus:
            uniques.add(fixed_seed)
            info = {
                "index":f"<span class='pla-results-init'>Init Spawn {init_spawn} </span></span>",
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
            if not isbonus:
                info["defaultroute"] = True
            else:
                info["defaultroute"] = False
            #print(info)
            storage[str(fixed_seed)]=info
    group_seed = main_rng.next()
    respawn_rng = XOROSHIRO(group_seed)
    for step_i,step in enumerate(steps):
        for pokemon in range(1,step+1):
            generator_seed = respawn_rng.next()
            respawn_rng.next() # spawner 1's seed, unused
            fixed_rng = XOROSHIRO(generator_seed)
            encounter_slot = (fixed_rng.next() / (2**64)) * encsum
            species,alpha = get_species(encounters,encounter_slot)
            if isbonus and alpha:
                guaranteed_ivs = 4
            elif isbonus or alpha:
                guaranteed_ivs = 3
            else:
                guaranteed_ivs = 0
            fixed_seed = fixed_rng.next()
            encryption_constant,pid,ivs,ability,gender,nature,shiny = \
                generate_from_seed(fixed_seed,rolls,guaranteed_ivs)
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
                if not isbonus and sum(steps[:step_i]) == len(steps[:step_i]) and pokemon == 1:
                    info["defaultroute"] = True
                else:
                    info["defaultroute"] = False
               # print(info)
                storage[str(fixed_seed)]=info
        respawn_rng = XOROSHIRO(respawn_rng.next())

def get_final(spawns):
    """Get the final path that will be generated to know when to stop aggressive recursion"""
    spawns -= 4
    path = [4] * (spawns // 4)
    if spawns % 4 != 0:
        path.append(spawns % 4)
    return path

def aggressive_outbreak_pathfind(group_seed,
                                 rolls,
                                 spawns,
                                 true_spawns,
                                 encounters,
                                 encsum,
                                 isbonus=False,
                                 isalpha=False,
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
            if aggressive_outbreak_pathfind(group_seed,
                                            rolls,
                                            spawns,
                                            true_spawns,
                                            encounters,
                                            encsum,
                                            isbonus,
                                            isalpha,
                                            _step,
                                            _steps,
                                            uniques,
                                            storage) is not None:
                return storage
    else:
        _steps.append(spawns - sum(_steps) - 4)
        generate_mass_outbreak_aggressive_path(group_seed,rolls,_steps,uniques,storage,spawns,true_spawns,encounters,encsum,isbonus,isalpha)
        if _steps == get_final(spawns):
            return storage
    return None

def next_filtered_aggressive_outbreak_pathfind(reader,group_seed,rolls,spawns,true_spawns,group_id,mapcount,isbonus,isalpha=False):
    """Check the next outbreak advances until an aggressive path to a pokemon that
       passes poke_filter exists"""
    encounters,encsum = get_encounter_table(reader,group_id,mapcount,isbonus)
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
        result = aggressive_outbreak_pathfind(group_seed, rolls, spawns,true_spawns,encounters,encsum,isbonus,isalpha)
        if result is None:
            result = []
    if advance == 0:
        info = result
    else:
        info = {
            "index":group_id,
            "spawn":False,
            "description":"Spawner not active"
            }
    if advance != 0:
        return info
    else:
        return info

def get_bonus_seed(reader,group_seed,rolls,mapcount,path,species,max_spawns):
    if species == 201:
        rolls = 19
        
    main_rng = XOROSHIRO(group_seed)
    for init_spawn in range(4):
        generator_seed = main_rng.next()
        main_rng.next() # spawner 1's seed, unused
    group_seed = main_rng.next()
    main_rng = XOROSHIRO(group_seed)
    respawn_rng = XOROSHIRO(group_seed)
    generator_seed = 0
    #for respawn in range(1,max_spawns-3):
    #print(f"Path: {path}")
    for respawn,step in enumerate(path):
        #print(f"Respawn: {respawn} Step {step}")
        for pokemon in range(0,step):
            #print(f"Pokemon {pokemon}")
            generator_seed = respawn_rng.next()
            tempseed = respawn_rng.next() # spawner 1's seed, unused
        respawn_rng = XOROSHIRO(respawn_rng.next())
    bonus_seed = (respawn_rng.next() - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF
        #bonus_seed = respawn_rng.next()
    #print(f"Bonus Seed: {bonus_seed:X}")
    return bonus_seed
    
def read_mass_outbreak_rng(reader,group_id,rolls,mapcount,species,group_seed,max_spawns,bonus_flag):
    if species == 201:
        rolls = 19
    print(f"Species Group: {SPECIES[species]}")
    
    true_spawns = max_spawns
    if bonus_flag:
        max_spawns = 10
    else:
        max_spawns += 3
    display = next_filtered_aggressive_outbreak_pathfind(reader,group_seed,rolls,max_spawns,true_spawns,group_id,mapcount,bonus_flag,False)
    return display

def get_encounter_table(reader,group_id,mapcount,bonus):
    encounters = {}
    encsum = 0
    if bonus:
        enc_pointer = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * mapcount+0x2c:X}",8)
    else:
        enc_pointer = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * mapcount+0x24:X}",8)

    enc_pointer = f"{enc_pointer:X}"
    enc_pointer = enc_pointer.upper()
    enc_pointer = "0x"+enc_pointer

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
            if alpha:
                slot = "Alpha "+slot
            return slot,alpha

    return "",False

def get_gen_seed_to_group_seed(reader,group_id):

    gen_seed = reader.read_pointer_int(f"[[[[[[main+42EEEE8]+78]+{0xD48 + group_id*0x8:X}]+58]+38]+478]+20",8)
    group_seed = (gen_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF

    return group_seed

def generate_mass_outbreak_aggressive_path_seed(group_seed,rolls,steps,uniques,storage,spawns,true_spawns,encounters,encsum,true_seed,isbonus=False,isalpha=False):
    """Generate all the pokemon of an outbreak based on a provided aggressive path"""
    # pylint: disable=too-many-locals, too-many-arguments
    # the generation is unique to each path, no use in splitting this function
    #group_seed = true_seed
    #print(f"True Seed: {group_seed:X}")
    respawns = true_spawns - 4
    main_rng = XOROSHIRO(group_seed)
    for init_spawn in range(4):
        generator_seed = main_rng.next()
        main_rng.next() # spawner 1's seed, unused
        fixed_rng = XOROSHIRO(generator_seed)
        encounter_slot = (fixed_rng.next() / (2**64)) * encsum
        species,alpha = get_species(encounters,encounter_slot)
        if isbonus and alpha:
            guaranteed_ivs = 4
        elif isbonus or alpha:
            guaranteed_ivs = 3
        else:
            guaranteed_ivs = 0
        fixed_seed = fixed_rng.next()
    group_seed = main_rng.next()
    respawn_rng = XOROSHIRO(group_seed)
    bonus_seed = respawn_rng
    for step_i,step in enumerate(steps):
       #print(f"Respawn {step_i}")
        for pokemon in range(1,step+1):
            #print(f"Pokemon {pokemon}")
            generator_seed = respawn_rng.next()
            seed = respawn_rng.next() # spawner 1's seed, unused
            fixed_rng = XOROSHIRO(generator_seed)
            #respawn_rng = XOROSHIRO(respawn_rng.next())
            encounter_slot = (fixed_rng.next() / (2**64)) * encsum
            species,alpha = get_species(encounters,encounter_slot)
            if isbonus and alpha:
                guaranteed_ivs = 4
            elif isbonus or alpha:
                guaranteed_ivs = 3
            else:
                guaranteed_ivs = 0
            fixed_seed = fixed_rng.next()
            level = fixed_rng.next()
        respawn_rng = XOROSHIRO(respawn_rng.next())

        #if ((steps[:step_i] + [pokemon]) not in uniques) and (sum(steps[:step_i]) + pokemon + 1) == true_spawns and ((sum(steps[:step_i]) + pokemon) - respawns) <=0:
        if ((steps[:step_i] + [pokemon]) not in uniques) and ((sum(steps[:step_i]) + pokemon) - respawns >=0 and (sum(steps[:step_i]) - respawns) < 0):
            add1 = steps[:step_i]
            addition = add1 + [pokemon]
            uniques.append(addition)
            #storage.append(seed)
            
        
        

def get_final_seed(spawns):
    """Get the final path that will be generated to know when to stop aggressive recursion"""
    spawns -= 4
    path = [4] * (spawns // 4)
    if spawns % 4 != 0:
        path.append(spawns % 4)
    return path

def aggressive_outbreak_pathfind_seed(group_seed,
                                 rolls,
                                 spawns,
                                 true_spawns,
                                 encounters,
                                 encsum,
                                 true_seed,
                                 isbonus=False,
                                 isalpha=False,
                                 step=0,
                                 steps=None,
                                 uniques=None,
                                 storage=None):
    """Recursively pathfind to possible shinies for the current outbreak via multi battles"""
    # pylint: disable=too-many-arguments
    # can this algo be improved?
    if steps is None or uniques is None or storage is None:
        steps = []
        uniques = []
        storage = []
    _steps = steps.copy()
    if step != 0:
        _steps.append(step)
    if sum(_steps) + step < spawns - 4:
        for _step in range(1, min(5, (spawns - 4) - sum(_steps))):
            if aggressive_outbreak_pathfind_seed(group_seed,
                                            rolls,
                                            spawns,
                                            true_spawns,
                                            encounters,
                                            encsum,
                                            true_seed,
                                            isbonus,
                                            isalpha,
                                            _step,
                                            _steps,
                                            uniques,
                                            storage) is not None:
                return uniques
    else:
        _steps.append(spawns - sum(_steps) -4 )
        generate_mass_outbreak_aggressive_path_seed(group_seed,rolls,_steps,uniques,storage,spawns,true_spawns,encounters,encsum,true_seed,isbonus,isalpha)
        if _steps == get_final_seed(spawns):
            return uniques
    return None

def next_filtered_aggressive_outbreak_pathfind_seed(reader,group_seed,rolls,spawns,true_spawns,group_id,mapcount,isbonus,true_seed,isalpha=False):
    """Check the next outbreak advances until an aggressive path to a pokemon that
       passes poke_filter exists"""
    encounters,encsum = get_encounter_table(reader,group_id,mapcount,isbonus)
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
        result = aggressive_outbreak_pathfind_seed(group_seed, rolls, spawns,true_spawns,encounters,encsum,true_seed,isbonus,isalpha)
        if result is None:
            result = []
    if advance == 0:
        info = result
    else:
        info = '\n'
    if advance != 0:
        return ""
    else:
        return info

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
        if _steps == get_final(spawns):
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
    group_seed = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * mapcount+0x44:X}",8)
    return group_seed

def get_max_spawns(reader,group_id,maps,isbonus):
    if isbonus:
        max_spawns = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * maps+0x60:X}",4)
    else:
        max_spawns = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * maps+0x4c:X}",4)

    return max_spawns

def get_map_name(reader,maps):

    mapname = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4 + 0xb80 * maps - 0x24:X}",2)
    mapname = f"{mapname:X}"
    mapname = mapnamevals.get(mapname, "None")

    return mapname

def get_bonus_flag(reader,group_id,maps):

    return True if reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * maps+0x18:X}",1) == 1 else False


def get_normal_outbreak_info(reader,group_id,inmap):
        species = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x20 + group_id*0x50:X}",2)
        if not inmap:
            group_seed = get_group_seed(reader,group_id,0)
        else:
            group_seed = get_gen_seed_to_group_seed(reader,group_id)
            
        max_spawns = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x20 + group_id*0x50+0x40:X}",8)

        coords = struct.unpack('fff',reader.read_pointer(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x20 + group_id*0x50+0x20:X}",12))

        coordinates = {
            "x":coords[0],
            "y":coords[1],
            "z":coords[2]
        }

        #print(coordinates)

        return species,group_seed,max_spawns,coordinates
                                      
def read_bonus_pathinfo(reader,paths,group_id,mapcount,rolls,group_seed,map_name,coords,true_spawns,bonus_spawns,max_spawns,species):
    isbonus = True
    outbreaks = {}
    for t,value in enumerate(paths):
        #print(f"Value: {value}, T: {t}")
        #print(f"True Spawns: {true_spawns} Bonus Spawns: {bonus_spawns} Max Spawns: {max_spawns}")
        seed = get_bonus_seed(reader,group_seed,rolls,mapcount,value,species,max_spawns)
        #print(f"Seed: {seed:X}")
        extra = [1] * (max_spawns - sum(value))
        for e,epath in enumerate(extrapaths):
            spawn_remain = max_spawns - sum(value)
            if epath == []:
                #print("Null path, this is doable.")
                #print(f"Null path, using seed {seed:X}")
                display = next_filtered_aggressive_outbreak_pathfind(reader,seed,rolls,bonus_spawns,true_spawns,group_id,mapcount,isbonus,False)
            elif epath[0] <= spawn_remain:
                #print("This is doable.")
                epath_seed = get_extra_path_seed(reader,seed,mapcount,epath)
                #print(f"Non null path, using seed {epath_seed:X}")
                display = next_filtered_aggressive_outbreak_pathfind(reader,epath_seed,rolls,bonus_spawns,true_spawns,group_id,mapcount,isbonus,False)
            else:
                #print(f"Remaining Spawns: {spawn_remain}, First epath: {epath[0]}, this is not doable. Continuing.")
                continue
            #print(f"Display: {display}")
            for index in display:
                form = ''
                #print(f"Index: {index}")
                #print(f"display[index]: {display[index]}")
                #display[index]["index"] = f"First Round Path: {value} + {extra} " + display[index]["index"]
                if epath == []:
                    display[index]["index"] = f"<span class='pla-results-firstpath'>First Round Path: {value} </span> + {extra} + <span class='pla-results-bonus'> Bonus " + display[index]["index"]
                else:
                    display[index]["index"] = f"<span class='pla-results-firstpath'>First Round Path: {value} </span> + <span class='pla-results-revisit'> Revisit {epath} </span> + <span class='pla-results-bonus'> Bonus " + display[index]["index"]
                display[index]["group"] = group_id
                display[index]["mapname"] = map_name
                display[index]["coords"] = coords
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
                #print(f"Species: {display[index]['species']}")
                #print(f"Cut Species: {cutspecies}")
                if display[index]["shiny"]:
                    spritename = f"c_{SPECIES.index(cutspecies)}{f'-{form}' if len(form) != 0 else ''}s.png"
                else:
                    spritename = f"c_{SPECIES.index(cutspecies)}{f'-{form}' if len(form) != 0 else ''}.png"
                display[index]["sprite"] = spritename
                if len(value) == sum(value):
                    display[index]["defaultroute"] = True
                else:
                    display[index]["defaultroute"] = False

            #print(f"Sprite: {display[index]['sprite']}")
            #print(f"Z: {z} Index: {index}")
            #print()
            outbreaks[f"Bonus" + f"{t} {value}" + f" {e} {epath}"] = display

    #print("Outbreaks:")
    #print()
    #print(outbreaks)
    return outbreaks
                                         
def get_map_mmos(reader,mapcount,rolls,inmap):
    outbreaks = {}
    print(f"Rolls: {rolls}")
    map_name = get_map_name(reader,mapcount)
    for i in range(0,16):
        enctable,_ = get_encounter_table(reader,i,mapcount,True)
        bonus_flag = False if enctable == None else True
        coords = read_group_coordinates(reader,i,mapcount)
        numspecies = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+i*0x90 + 0xb80 * mapcount:X}",2)
        if numspecies != 0:
            if not inmap:
                group_seed = get_group_seed(reader,i,mapcount)
            else:
                group_seed = get_gen_seed_to_group_seed(reader,i)
            #print(f"Group seed for {i} is {group_seed:X}")
            max_spawns = get_max_spawns(reader,i,mapcount,False)
            display = read_mass_outbreak_rng(reader,i,rolls,mapcount,numspecies,group_seed,max_spawns,False)
            for index in display:
                if index != "index" and index != "description":
                    form = ''
                    display[str(index)]["group"] = i
                    display[str(index)]["mapname"] = map_name
                    display[str(index)]["coords"] = coords
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
                    #print(f"Species: {display[str(index)]['species']}")
                    #print(f"Cut Species: {cutspecies}")
                    if display[str(index)]["shiny"]:
                        spritename = f"c_{SPECIES.index(cutspecies)}{f'-{form}' if len(form) != 0 else ''}s.png"
                    else:
                        spritename = f"c_{SPECIES.index(cutspecies)}{f'-{form}' if len(form) != 0 else ''}.png"
                    display[str(index)]["sprite"] = spritename

                    #print(f"Sprite: {display[str(index)]['sprite']}")
            if bonus_flag:
                true_spawns = max_spawns
                #print(f"True_spawns = {true_spawns}")
                bonus_spawns = true_spawns + 4
                #print(f"Max_spawns = {max_spawns}")
                #paths = next_filtered_aggressive_outbreak_pathfind_seed(reader,group_seed,rolls,max_spawns,true_spawns,i,mapcount,bonus_flag,group_seed,False)
                bonus_seed = next_filtered_aggressive_outbreak_pathfind_seed(reader,group_seed,rolls,bonus_spawns,true_spawns,i,mapcount,bonus_flag,False)
                #print(f"Paths: {bonus_seed}")
                #print(f"Path length: {len(bonus_seed)}")
                true_spawns = get_max_spawns(reader,i,mapcount,True)
                result = read_bonus_pathinfo(reader,bonus_seed,i,mapcount,rolls,group_seed,map_name,coords,true_spawns,bonus_spawns,max_spawns,numspecies)
                print(f"Group {i} Bonus Complete!")
            #print(f"Display: {display}")
            outbreaks[f"{i} " + f"{bonus_flag}"] = display
            print(f"Group {i} Complete!")
            if bonus_flag:
                outbreaks[f"{i} " + f"{bonus_flag}" + "bonus"] = result
        else:
            continue
            
    return outbreaks

def get_all_map_mmos(reader,rolls,inmap):
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
    #print(display)
    return display


def get_all_map_names(reader):
    maps = []
    for i in range(0,4):
        map_name = get_map_name(reader,i)
        maps.append(map_name)

    return maps

def read_normal_outbreaks(reader,rolls,inmap):
    outbreaks = {}
    rolls = rolls + 13
    print(f"Rolls: {rolls}")
    for i in range(0,4):
        species,group_seed,max_spawns,coordinates = get_normal_outbreak_info(reader,i,inmap)
        if species != 0:
            display = next_filtered_aggressive_outbreak_pathfind_normal(group_seed,rolls,max_spawns)
            for index in display:
                if index != "index" and index != "description":
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
                        #print(f"Form: {form} cutspecies: {cutspecies}")
                    else:
                        cutspecies = display[str(index)]["species"]
                    #print(f"Form: {form} cutspecies: {cutspecies}")
                    #print(f"Species: {display[index]['species']}")
                    #print(f"Cut Species: {cutspecies}")
                    if display[str(index)]["shiny"]:
                        spritename = f"c_{SPECIES.index(cutspecies)}{f'-{form}' if len(form) != 0 else ''}s.png"
                    else:
                        spritename = f"c_{SPECIES.index(cutspecies)}{f'-{form}' if len(form) != 0 else ''}.png"
                    display[str(index)]["sprite"] = spritename

                    #print(f"Sprite: {display[str(index)]['sprite']}")
            outbreaks[f"Outbreak {i}"] = display

    return outbreaks


def get_all_outbreak_names(reader,inmap):
    outbreaks = []
    for i in range(0,4):
        species,_,_,_ = get_normal_outbreak_info(reader,i,inmap)
        if species != 0:
            outbreaks.append(SPECIES[species])

    return outbreaks

def read_group_coordinates(reader,group_id,mapcount):

    """
    x_coord = reader.read_pointer(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * mapcount - 0x14:X}",4)
    y_coord = reader.read_pointer(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * mapcount - 0x10:X}",4)
    z_coord = reader.read_pointer(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * mapcount - 0x0c:X}",4)

    x = struct.unpack('f',x_coord)
    y = struct.unpack('f',y_coord)
    z = struct.unpack('f',z_coord)

    print(f"X: {x} Y: {y} Z: {z}")
    """
    
    #print(f"Z Pointer: [[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * mapcount - 0x14:X}")
    coords = struct.unpack('fff',reader.read_pointer(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * mapcount - 0x14:X}",12))

    coordinates = {
        "x":coords[0],
        "y":coords[1],
        "z":coords[2]
        }
                           

    #print(coordinates)
    
    return coordinates

def teleport_to_spawn(reader,coords):
    cordarray = []
    PLAYER_PTR = f"[[[[[[main+42D4720]+18]+48]+1F0]+18]+370]+90"

    #print(f"Teleporting to {coords}")

    for c in coords:
        cordarray.append(coords[c])

    print(f"Teleporting to {cordarray}")
    position_bytes = struct.pack('fff', *cordarray)
    
    #reader.write_pointer(PLAYER_PTR,f"{int.from_bytes(position_bytes,'big'):024X}")
    reader.write_pointer(PLAYER_PTR,f"{int.from_bytes(position_bytes,'big'):024X}")


def get_extra_path_seed(reader,group_seed,mapcount,path):
        main_rng = XOROSHIRO(group_seed)
        respawn_rng = XOROSHIRO(group_seed)
        generator_seed = 0
        for respawn,step in enumerate(path):
            #print(f"Respawn: {respawn} Step {step}")
            for pokemon in range(0,(4 -step)):
                #print(f"Pokemon {pokemon}")
                generator_seed = respawn_rng.next()
                tempseed = respawn_rng.next() # spawner 1's seed, unused
            respawn_rng = XOROSHIRO(respawn_rng.next())
        bonus_seed = (respawn_rng.next() - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF
        #bonus_seed = respawn_rng.next()
        return bonus_seed
