# Go to root of PyNXReader
import sys
import json
import struct

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
                "index":f"Init Spawn {init_spawn}",
                "spawn":True,
                "generator_seed":generator_seed,
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
                "index":f"Path: {'|'.join(str(s) for s in steps[:step_i] + [pokemon])}",
                "spawn":True,
                "generator_seed":generator_seed,
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

def get_bonus_seed(reader,group_id,rolls,mapcount,path):
    species = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * mapcount:X}",2)
    #print(f"Species Pointer: [[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * mapcount:X}")
    if species != 0:
        if species == 201:
            rolls = 19
        group_seed = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * mapcount+0x44:X}",8)
        max_spawns = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * mapcount+0x60:X}",4)
        #print(f"Max spawns: {max_spawns}")
        curr_spawns = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * mapcount+0x50:X}",4)
        main_rng = XOROSHIRO(group_seed)
        for init_spawn in range(4):
            generator_seed = main_rng.next()
            main_rng.next() # spawner 1's seed, unused
            fixed_rng = XOROSHIRO(generator_seed)
            fixed_rng.next()
            fixed_seed = fixed_rng.next()
            ec,pid,ivs,ability,gender,nature,shiny = generate_from_seed(fixed_seed,rolls)
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
                fixed_rng = XOROSHIRO(generator_seed)
                fixed_rng.next()
                fixed_seed = fixed_rng.next()
                ec,pid,ivs,ability,gender,nature,shiny = generate_from_seed(fixed_seed,rolls)
                fixed_seed = fixed_rng.next()
            respawn_rng = XOROSHIRO(respawn_rng.next())
        bonus_seed = (respawn_rng.next() - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF
            #bonus_seed = respawn_rng.next()
        #print(f"Bonus Seed: {bonus_seed:X}")
        return bonus_seed
    else:
        #print()
        return None
    
def read_mass_outbreak_rng(reader,group_id,rolls,mapcount,bonus_flag):
    species = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+group_id*0x90 + 0xb80 * mapcount:X}",2)
    if species != 0:
        if species == 201:
            rolls = 19
        print(f"Species Group: {SPECIES[species]}")
        group_seed = get_group_seed(reader,group_id,mapcount)
        max_spawns = get_max_spawns(reader,group_id,mapcount,bonus_flag)
        
        true_spawns = max_spawns
        if bonus_flag:
            max_spawns = 10
        else:
            max_spawns += 3
        display = next_filtered_aggressive_outbreak_pathfind(reader,group_seed,rolls,max_spawns,true_spawns,group_id,mapcount,bonus_flag,False)
        return display
    else:
        display = {
            "index":group_id,
            "description":"Spawner not active"
            }
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
                "index":f"Init Spawn {init_spawn}",
                "spawn":True,
                "generator_seed":generator_seed,
                "shiny":shiny,
                "alpha":alpha,
                "ec":encryption_constant,
                "pid":pid,
                "ivs":ivs,
                "ability":ability,
                "nature":NATURES[nature],
                "gender":gender
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
                "index":f"Path: {'|'.join(str(s) for s in steps[:step_i] + [pokemon])}",
                "spawn":True,
                "generator_seed":generator_seed,
                "shiny":shiny,
                "alpha":alpha,
                "ec":encryption_constant,
                "pid":pid,
                "ivs":ivs,
                "ability":ability,
                "nature":NATURES[nature],
                "gender":gender
                }
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


def get_normal_outbreak_info(reader,group_id):
        species = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x20 + group_id*0x50:X}",2)
        group_seed = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x20 + group_id*0x50+0x38:X}",8)
        max_spawns = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x20 + group_id*0x50+0x40:X}",8)

        coords = struct.unpack('fff',reader.read_pointer(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x20 + group_id*0x50+0x20:X}",12))

        coordinates = {
            "x":coords[0],
            "y":coords[1],
            "z":coords[2]
        }

        print(coordinates)

        return species,group_seed,max_spawns,coordinates
                                      
def read_bonus_pathinfo(reader,paths,group_id,mapcount,rolls,group_seed,map_name,coords):
    isbonus = True
    outbreaks = {}
    max_spawns = 10
    true_spawns = get_max_spawns(reader,group_id,mapcount,True)
    for t,value in enumerate(paths):
        #print(f"Value: {value}, T: {t}")
        seed = get_bonus_seed(reader,group_id,rolls,mapcount,value)
        #print(f"Seed: {seed:X}")
        extra = [1] * (get_max_spawns(reader,group_id,mapcount,False) - sum(value))
        display = next_filtered_aggressive_outbreak_pathfind(reader,seed,rolls,max_spawns,true_spawns,group_id,mapcount,isbonus,False)
        #print(f"Display: {display}")
        for index in display:
            #print(f"Index: {index}")
            #print(f"display[index]: {display[index]}")
            #display[index]["index"] = f"First Round Path: {value} + {extra} " + display[index]["index"]
            display[index]["index"] = f"First Round Path: {value} + {extra} Bonus " + display[index]["index"]
            display[index]["group"] = group_id
            display[index]["mapname"] = map_name
            display[index]["coords"] = coords
            #print(f"Z: {z} Index: {index}")
            #print()
        outbreaks[f"Bonus" + f"{t} {value}"] = display

    #print("Outbreaks:")
    #print()
    #print(outbreaks)
    return outbreaks
                                         
def get_map_mmos(reader,mapcount,rolls):
    outbreaks = {}
    print(f"Rolls: {rolls}")
    map_name = get_map_name(reader,mapcount)
    for i in range(0,16):
        enctable,_ = get_encounter_table(reader,i,mapcount,True)
        bonus_flag = False if enctable == None else True
        coords = read_group_coordinates(reader,i,mapcount)
        display = read_mass_outbreak_rng(reader,i,rolls,mapcount,False)
        for index in display:
            if index != "index" and index != "description":
                display[str(index)]["group"] = i
                display[str(index)]["mapname"] = map_name
                display[str(index)]["coords"] = coords
        if bonus_flag:
            true_spawns = get_max_spawns(reader,i,mapcount,False)
            #print(f"True_spawns = {true_spawns}")
            max_spawns = true_spawns + 4
            #print(f"Max_spawns = {max_spawns}")
            group_seed = get_group_seed(reader,i,mapcount)
            #paths = next_filtered_aggressive_outbreak_pathfind_seed(reader,group_seed,rolls,max_spawns,true_spawns,i,mapcount,bonus_flag,group_seed,False)
            bonus_seed = next_filtered_aggressive_outbreak_pathfind_seed(reader,group_seed,rolls,max_spawns,true_spawns,i,mapcount,bonus_flag,group_seed,False)
            #print(f"Paths: {bonus_seed}")
            #print(f"Path length: {len(bonus_seed)}")
            result = read_bonus_pathinfo(reader,bonus_seed,i,mapcount,rolls,group_seed,map_name,coords)
            print(f"Group {i} Bonus Complete!")
        #print(f"Display: {display}")
        outbreaks[f"{i} " + f"{bonus_flag}"] = display
        print(f"Group {i} Complete!")
        if bonus_flag:
            outbreaks[f"{i} " + f"{bonus_flag}" + "bonus"] = result
            
    return outbreaks

def get_all_map_mmos(reader,rolls):
    display = {}
    for i in range(0,4):
        map_name = get_map_name(reader,i)
        print(f"Map {map_name} starting now...")
        result = get_map_mmos(reader,i,rolls)
        display[map_name] = result
        print(f"Map {map_name} complete!")

    #print(display)
    return display


def get_all_map_names(reader):
    maps = []
    for i in range(0,4):
        map_name = get_map_name(reader,i)
        maps.append(map_name)

    return maps

def read_normal_outbreaks(reader,rolls):
    outbreaks = {}
    rolls = rolls + 13
    print(f"Rolls: {rolls}")
    for i in range(0,4):
        species,group_seed,max_spawns,coordinates = get_normal_outbreak_info(reader,i)
        if species != 0:
            display = next_filtered_aggressive_outbreak_pathfind_normal(group_seed,rolls,max_spawns)
            for index in display:
                if index != "index" and index != "description":
                    display[str(index)]["group"] = i
                    display[str(index)]["mapname"] = "Normal Outbreak"
                    display[str(index)]["species"] = SPECIES[species]
                    display[str(index)]["coords"] = coordinates
            outbreaks[f"Outbreak {i}"] = display

    return outbreaks


def get_all_outbreak_names(reader):
    outbreaks = []
    for i in range(0,4):
        species,_,_ = get_normal_outbreak_info(reader,i)
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


"""       
if __name__ == "__main__":
    #rolls = int(input("Shiny Rolls For Species: "))
    #maps = int(input("Map Count: "))
    print(f"Rolls: {rolls}")
    aggro = True if defaultaggro else False
    #initial = False if input("Are you in the map? Y/N: ").lower() == 'n' else True
    display = []
    mapname = "Unknown"

    for maps in range(0,5):
        for i in range(0,15):
            if i == 0:
                mapname = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4 + 0xb80 * maps - 0x24:X}",2)
                #print(f"Mapname pointer: [[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+i*0x90 + 0xb80 * maps - 0x24:X}")
                #print(f"Mapname: {mapname:X}")
                mapname = f"{mapname:X}"
                mapname = mapnamevals.get(mapname, "Forbidden Zone")
                #print(f"Mapname: {mapname}")
            print()
            print(f"Checking group {i}, in the {mapname}: ")
            print()
            bonus_flag = True if reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+i*0x90 + 0xb80 * maps+0x18:X}",1) == 1 else False
            display = read_mass_outbreak_rng(i,rolls,maps,aggro,bonus_flag)
            if display is None:
                break
            elif display is [1]:
                continue
            else:
                if aggro:
                    for p in range(0,len(display)):
                        if display[p] != 1:
                            print(display[p])
                    #bonus_seed = get_bonus_seed(i,rolls,maps)
                    #if bonus_seed is None:
                       # break
                    if bonus_flag:
                        print(f"Bonus Flag: {bonus_flag}")
                        isbonus = True
                        #true_spawns = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+i*0x90 + 0xb80 * maps+0x60:X}",4)
                        true_spawns = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+i*0x90 + 0xb80 * maps+0x4c:X}",4)
                        extra_count = true_spawns
                        max_spawns = true_spawns+4
                        group_seed = get_group_seed(i,maps)
                        
                        paths,bonus_seeds = next_filtered_aggressive_outbreak_pathfind_seed(group_seed,rolls,max_spawns,true_spawns,i,isbonus,group_seed,False)
                        true_spawns = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+i*0x90 + 0xb80 * maps+0x60:X}",4)
                        max_spawns = 10
                        #print(paths)
                        #print(bonus_seed)
                        #print(len(paths))
                        print(f" Total Paths found: {len(bonus_seed)}")
                        
                        for t,value in enumerate(bonus_seed):
                            #print(f"Seed: {value}")
                            #print(f"Path {value}:")
                            seed = get_bonus_seed(i,rolls,maps,value)
                            extras = extra_count - sum(value)
                            extras = [1] * extras
                            #print(f"Seed: {seed:X}")
                            nonalpha = [next_filtered_aggressive_outbreak_pathfind(seed,rolls,max_spawns,true_spawns,i,isbonus,False)]
                            #print(nonalpha[0])
                            if "Nothing found" not in nonalpha[0]:
                                for v in range(0,len(nonalpha)):
                                    print()
                                    print(f" First Round Path: {value} + {extras}\n")
                                    print(nonalpha[v])
                        
                        print(f"Bonus Round:")
                        for q in range(0,len(nonalpha)):
                            print(nonalpha[q])
"""
