import json
import struct
from datetime import datetime
from app import RESOURCE_PATH
from pla.core import BASE_ROLLS_MMOS, generate_from_seed, get_rolls, get_sprite
from pla.data import pokedex, natures
from pla.rng import XOROSHIRO

MAX_MAPS = 5
MAX_MMOS = 16

mapnamevals = {
    "5504":"Crimson Mirelands",
    "5351":"Alabaster Icelands",
    "519E":"Coronet Highlands",
    "5A1D":"Obsidian Fieldlands",
    "56B7":"Cobalt Coastlands"}

encmap = json.load(open(RESOURCE_PATH + "resources/mmo_es.json"))

allpaths = json.load(open(RESOURCE_PATH + "resources/mmopaths.json"))

nonbonuspaths = json.load(open(RESOURCE_PATH + "resources/nonbonuspaths.json"))

extrapaths = [[],[1],[2],[2,1],[3],[3,1],[3,2],[3,2,1]]

initchain = ["<span class='pla-results-init'>Initial Spawn 4 </span></span>","<span class='pla-results-init'>Initial Spawn 3 </span></span>",
              "<span class='pla-results-init'>Initial Spawn 2 </span></span>","<span class='pla-results-init'>Initial Spawn 1 </span></span>"]

def generate_mmo_aggressive_path(group_seed,research,paths,max_spawns,true_spawns,
                                           encounters,encsum,dupestore,chained,isbonus=False,rolls_override=None):
    """Generate all the pokemon of an outbreak based on a provided aggressive path"""
    # pylint: disable=too-many-locals, too-many-arguments
    # the generation is unique to each path, no use in splitting this function
    storage = {}
    uniques = set()

    main_rng = XOROSHIRO(group_seed)
    for init_spawn in range(1,5):
        generator_seed = main_rng.next()
        main_rng.next()
        fixed_rng = XOROSHIRO(generator_seed)
        encounter_slot = (fixed_rng.next() / (2**64)) * encsum
        fixed_seed = fixed_rng.next()
        
        if fixed_seed not in uniques:
            uniques.add(fixed_seed)
            path_id = get_path_id(fixed_seed, init_spawn)
            dupestore[str(fixed_seed)] = path_id

            pokemon, alpha = get_species(encounters,encounter_slot)
            fixed_gender = pokemon.is_fixed_gender()
            guaranteed_ivs = get_guaranteed_ivs(alpha, isbonus)
            rolls = rolls_override if rolls_override is not None else get_rolls(pokemon, research, BASE_ROLLS_MMOS)
            ec,pid,ivs,ability,gender,nature,shiny,square = \
                generate_from_seed(fixed_seed, rolls, guaranteed_ivs, fixed_gender)
            gender = pokemon.calculate_gender(gender)

            storage[path_id] = {
                "index": f"<span class='pla-results-init'>Initial Spawn {init_spawn} </span></span>",
                "generator_seed": generator_seed,
                "species": pokemon.display_name(),
                "sprite": get_sprite(pokemon, shiny, gender),
                "shiny": shiny,
                "square": square,
                "alpha": alpha,
                "ec": ec,
                "pid": pid,
                "ivs": ivs,
                "ability": ability,
                "nature": natures(nature),
                "gender": gender.value,
                "rolls": rolls,
                "dupes": [],
                "chains": [],
                "defaultroute": not isbonus,
                "multi": False
            }
    
    respawn_seed = main_rng.next()
    for path_num, path in enumerate(paths):
        respawn_rng = XOROSHIRO(respawn_seed)
        for step_num, step in enumerate(path):
            for spawn_on_step in range(1, step + 1):
                generator_seed = respawn_rng.next()
                respawn_rng.next()
                fixed_rng = XOROSHIRO(generator_seed)
                encounter_slot = (fixed_rng.next() / (2**64)) * encsum
                fixed_seed = fixed_rng.next()
                
                if fixed_seed not in uniques:
                    uniques.add(fixed_seed)
                    path_id = get_path_id(fixed_seed, path[:step_num] + [spawn_on_step], path_num, path)
                    dupestore[fixed_seed] = path_id

                    pokemon, alpha = get_species(encounters, encounter_slot)
                    fixed_gender = pokemon.is_fixed_gender()
                    guaranteed_ivs = get_guaranteed_ivs(alpha, isbonus)
                    rolls = rolls_override if rolls_override is not None else get_rolls(pokemon, research, BASE_ROLLS_MMOS)
                    ec,pid,ivs,ability,gender,nature,shiny,square = \
                        generate_from_seed(fixed_seed, rolls, guaranteed_ivs, fixed_gender)
                    gender = pokemon.calculate_gender(gender)

                    storage[path_id] = {
                        "index": get_path_string(path[:step_num], spawn_on_step),
                        "generator_seed": generator_seed,
                        "species": pokemon.display_name(),
                        "sprite": get_sprite(pokemon, shiny, gender),
                        "shiny": shiny,
                        "square": square,
                        "alpha": alpha,
                        "ec": ec,
                        "pid": pid,
                        "ivs": ivs,
                        "ability": ability,
                        "nature": natures(nature),
                        "gender": gender.value,
                        "rolls": rolls,
                        "dupes": [],
                        "chains": [],
                        "defaultroute": not isbonus and sum(path[:step_num]) == len(path[:step_num]) and spawn_on_step == 1,
                        "multi": False
                    }
                else:
                    path_str = get_path_string(path[:step_num], step)
                    dupemon = storage[dupestore[fixed_seed]]
                    
                    if path_str != dupemon['index'] \
                       and path_str != get_path_string(path[:step_num], spawn_on_step) \
                       and step + 1 - spawn_on_step < 3:
                        
                        ghosts = sum(path[:step_num]) + spawn_on_step - (true_spawns - 4)
                        
                        if ghosts <= 0:
                            dupemon["dupes"].append(get_path_string(path))
            
            respawn_rng = XOROSHIRO(respawn_rng.next())
    return storage

def get_path_id(seed, spawn, i=None, steps=None):
    if i is None and steps is None:
        return f"{seed:X} + {spawn}"
    return f"{seed:X} + {spawn} + {i} + {steps}"

def get_path_string(steps, final = None):
    return "Path: " + ', '.join(f"D{step}" for step in (steps if final is None else steps + [final]))
    
def get_guaranteed_ivs(alpha, isbonus):
    if isbonus and alpha:
        return 4
    if isbonus or alpha:
        return 3
    return 0

def get_species(encounters, encounter_slot):
    encsum = 0
    for slot in encounters:
        encsum += slot['slot']
        if encounter_slot < encsum:
            return pokedex.entry(slot['name']), slot['alpha']
    return None, False

def get_encounter_table(enc_pointer):
    if enc_pointer not in encmap:
        return None, 0
    
    encounters = encmap[enc_pointer]
    encsum = sum(e['slot'] for e in encounters)
    return encounters, encsum

def get_map_name(reader, map_index):
    map_id = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                     f"{0x1d4 + 0xb80*map_index - 0x24:X}", 2)
    return mapnamevals.get(f"{map_id:X}", None)

def get_all_map_names(reader):
    """gets all map names"""
    return [get_map_name(reader, map_index) for map_index in range(MAX_MAPS)]

def get_all_map_mmo_info(reader):
    res = {}
    for map_index in range(MAX_MAPS):
        map_name = get_map_name(reader, map_index)
        if map_name is not None:
            res[map_name] = get_map_mmo_info(reader, map_index, map_name)
    return res

def get_map_mmo_info(reader, map_index, map_name=None):
    res = []
    for group_id in range(MAX_MMOS):
        mmoinfo = get_mmo_info(reader, map_index, group_id)
        
        if mmoinfo['species_index'] != 0:
            mmoinfo['pokemon'] = pokedex.entry_by_index(mmoinfo['species_index'])
            
            if map_name is not None:
                mmoinfo['map_name'] = map_name
            res.append(mmoinfo)

    return res

def get_mmo_info(reader, map_index, group_id):
    data = reader.read_pointer(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1c0 + 0xb80*map_index + 0x90*group_id:X}", 0x78)
    return {
        'map_index': map_index,
        'group_id': group_id,
        'species_index': int.from_bytes(data[0x14:0x14+2], 'little'),
        'fr_encounter': f"0x{int.from_bytes(data[0x38:0x38+8], 'little'):X}",
        'fr_spawns': int.from_bytes(data[0x60:0x60+4], 'little'),  
        'has_bonus': int.from_bytes(data[0x2c:0x2c+1], 'little') == 1,
        'br_encounter': f"0x{int.from_bytes(data[0x40:0x40+8], 'little'):X}",
        'br_spawns': int.from_bytes(data[0x74:0x74+4], 'little'),
        'coords': struct.unpack('fff', data[0x0:0x0+12]),
        'group_seed': int.from_bytes(data[0x58:0x58+8], 'little'),
        'num_spawned': int.from_bytes(data[0x64:0x64:4], 'little')
    }

def get_seed_spawned(reader, map_index, group_id):
    data = reader.read_pointer(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x218 + 0xb80*map_index + 0x90*group_id:X}", 0x10)
    return {
        'seed': int.from_bytes(data[0:8], 'little'),
        'num_spawned': int.from_bytes(data[12:16, 'little'])
    }

# These methods could potentially go it is almost as fast to read all at the same time as to read one,
# And faster to real them all at the same time than to read two seperately
def get_encounter_pointer(reader, map_index, group_id, bonus):
    offset = 0x2c if bonus else 0x24
    enc_pointer = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                              f"{0x1d4 + 0xb80*map_index + 0x90*group_id + offset:X}", 8)
    return f"0x{enc_pointer:X}"

def get_group_seed(reader, map_index, group_id):
    return reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                         f"{0x1d4 + 0xb80*map_index + 0x90*group_id + 0x44:X}", 8)

def get_gen_seed_to_group_seed(reader,group_id):
    gen_seed = reader.read_pointer_int(f"[[[[[[main+42EEEE8]+78]+" \
                                       f"{0xD48 + 0x8*group_id:X}]+58]+38]+478]+20", 8)
    return (gen_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF

def get_max_spawns(reader, map_index, group_id, isbonus):
    offset = 0x60 if isbonus else 0x4c
    return reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                             f"{0x1d4 + 0xb80*map_index + 0x90*group_id + offset:X}", 4)

def get_bonus_flag(reader, map_index, group_id):
    return reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                   f"{0x1d4 + 0xb80*map_index + 0x90*group_id + 0x18:X}", 1) == 1

def get_group_coordinates(reader, map_index, group_id):
    """reads coordinates of mmo group"""
    coords = struct.unpack('fff', reader.read_pointer(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                                      f"{0x1d4 + 0xb80*map_index + 0x90*group_id - 0x14:X}", 12))
    coordinates = {
        "x":coords[0],
        "y":coords[1],
        "z":coords[2]
    }
    return coordinates

def get_num_spawned(reader, map_index, group_id):
    return reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4 + 0xb80*map_index + 0x90*group_id + 0x64:X}", 4)
# End possible deletions

def get_nonbonus_paths(max_spawns):
    return nonbonuspaths[str(max_spawns)]

def get_bonus_paths(max_spawns):
    return allpaths[str(max_spawns)]

def get_bonus_seed(group_seed, path):
    main_rng = XOROSHIRO(group_seed)
    for _ in range(4):
        main_rng.next()
        main_rng.next()
    group_seed = main_rng.next()
    respawn_rng = XOROSHIRO(group_seed)
    for step in path:
        for _ in range(0,step):
            respawn_rng.next()
            respawn_rng.next()
        respawn_rng = XOROSHIRO(respawn_rng.next())
    return (respawn_rng.next() - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF

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

def format_firstround_result(result,group_id,map_name,coords,max_spawns,chained):
    result["group"] = group_id
    result["mapname"] = map_name
    result["coords"] = coords
    result["numspawns"] = max_spawns
    
    if result["shiny"]:
        chained[result["index"]] = f"<span class='pla-results-firstpath'>First Round </span>{result['index']}"
        print(f"Chained: {chained}")

def format_bonusround_result(result,path,epath,group_id,map_name,coords,true_spawns,max_spawns,chained):
    result["index"] = get_bonusround_path_display(result["index"], path, epath)
    result["group"] = group_id
    result["mapname"] = map_name
    result["coords"] = coords
    result["numspawns"] = max_spawns
    result["defaultroute"] = len(path) == sum(path)
    
    for i in range(len(result["dupes"])):
        result["dupes"][i] = f"Bonus {result['dupes'][i]} "

    if result["shiny"]:
        chainstring = result["index"].rpartition("Bonus")[0]
        chainresult = []
        frchainstring = result["index"].split('+')[0]
        frchainstring = frchainstring[:frchainstring.rfind("</span>")-1].replace('[','').replace(']','').replace(', ','').split("D")[1:]
        #print(f"frChainstring: {frchainstring}")
        for chain in chained:
            if "+" not in chain and "Initial" not in chain:
                frpath = chain.replace(', ','').split("D")[1:]
                frbonuspath = list(map(int,frchainstring))
                frpath = list(map(int,frpath))
                #print(f"frpath: {frpath}")
                #print(f"frbonuspath: {frbonuspath}")
                if len(frpath) <= len(frbonuspath):
                    remain = max_spawns - 4
                    match = True
                    for v in range(0,len(frpath)-1):
                        remain = remain - frpath[v]
                        if frpath[v] != frbonuspath[v]:
                            match = False
                    if match:
                        if len(frpath) == len(frbonuspath) and frpath[len(frpath)-1] == frbonuspath[len(frbonuspath)-1]:
                            print("Exact first round path, adding")
                            result["chains"].append(chained[chain])
                        elif frbonuspath[len(frpath)-1] >= frpath[len(frpath)-1]:
                            difference = frbonuspath[len(frpath)-1] - frpath[len(frpath)-1]
                            if remain > difference or difference == 0:
                                print("Bonus Path > frpath, adding")
                                result["chains"].append(chained[chain])
        #print(f"Chainstring: {chainstring}")
        if chained.get(chainstring, None) is not None:
            chainresult.append(chainstring)
        for ini,initcha in enumerate(initchain):
            if chained.get(initcha, None) is not None:
                chainresult.append(initcha)
        for r,res in enumerate(chainresult):
            """
            if res is not None and (res.rpartition('Bonus')[0] == f"<span class='pla-results-firstpath'>" + \
                                    f"First Round Path: " + \
                                    f"{string} </span> + [Clear Round]+ " + \
                                    f"<span class='pla-results-bonus'> "
                                    or res.rpartition('Bonus')[0] == f"<span class='pla-results-firstpath'>First Round Path: " + \
                                    f"{string} </span> + <span class='pla-results-revisit'> " + \
                                    f"Revisit {epath} </span> + <span class='pla-results-bonus'> "):
            """
            if res is not None:
                print("Possible Chain Shiny Found!")
                bonuscheck = chained[res].rpartition("Bonus Path:")[2].replace(" ",'').replace("D",'').split(',')
                print(f"Bonus Check: {bonuscheck}")
                currcheck = result["index"].rpartition("Bonus Path:")[2].replace(" ",'').replace("D",'').split(',')
                print(f"Curr Check: {currcheck}")
                #print(f"Initial in? {'Initial' in bonuscheck[len(bonuscheck)-1]}")
                if "Initial" in bonuscheck[len(bonuscheck)-1] or "FirstRound" in bonuscheck[0] or (len(bonuscheck) < len(currcheck) and bonuscheck[0] == currcheck[0]):
                    print("Either an initial spawn, or bonuscheck < currcheck and they're on the same path, adding.")
                    result["chains"].append(chained[res])
                elif len(bonuscheck) < len(currcheck):
                    bonuscheck = list(map(int, bonuscheck))
                    currcheck = list(map(int, currcheck))
                    respawns = true_spawns - 4
                    remain = respawns
                    for t in range(0,len(bonuscheck)):
                        remain = remain - bonuscheck[t]
                    if remain >= 1:
                        print("Remaining >1, adding")
                        result["chains"].append(chained[res])
                elif len(bonuscheck) == len(currcheck) and bonuscheck[0] == currcheck[0]:
                    bonuscheck = list(map(int, bonuscheck))
                    currcheck = list(map(int, currcheck))
                    max_path_size = max(sum(bonuscheck),sum(currcheck))
                    print(f"Max Path: {max_path_size}")
                    respawns = true_spawns - 4
                    print(f"respawns: {respawns}")
                    ghosts = max_path_size - respawns
                    print(f"Ghosts: {ghosts}")
                    difference = max_path_size - min(sum(bonuscheck),sum(currcheck))
                    print(f"Difference: {difference}")
                    if ghosts < 0:
                        print("Ghosts < 0, adding to chain")
                        result["chains"].append(chained[res])
                    else:
                        pokesleft = respawns
                        for i in range(0,len(currcheck)-1):
                            pokesleft = pokesleft - currcheck[i]
                        print(f"Amount left: {pokesleft}")
                        if (pokesleft <= 0) and not difference >= 2:
                            print(f"Pokesleft <=0 and Difference < 2, adding")
                            result["chains"].append(chained[res])
                        elif pokesleft > 1 and difference < pokesleft:
                            print(f"Pokesleft >0 and difference = {difference}, adding")
                            result["chains"].append(chained[res])
                        else:
                            print(f"Pokesleft not <=0 or difference >= 2.")
        chained[result["index"].rpartition("Bonus")[0]] = result["index"]

def get_bonusround_path_display(index, path, epath):
    path_string = '[' + ', '.join(f"D{v}" for v in path) + ']'
    epath_string = "[Clear Round]" if epath == [] else f"<span class='pla-results-revisit'> Revisit {epath} </span>"
    return (
        f"<span class='pla-results-firstpath'>First Round Path: {path_string}</span>"
        f" + {epath_string} + <span class='pla-results-bonus'> Bonus {index}"
    )

def get_bonusround(paths,group_id,research,group_seed,map_name,coords,
                    true_spawns,bonus_spawns,max_spawns,encounters,encsum,chained,rolls_override=None):
    #pylint: disable=too-many-branches
    """reads info about a bonus path"""
    outbreaks = {}
    dupestore = {}
    nbpaths = get_nonbonus_paths(true_spawns)

    for path_num, path in enumerate(paths):
        seed = get_bonus_seed(group_seed,path)
        
        for ext_num, epath in enumerate(extrapaths):
            spawn_remain = max_spawns - sum(path)
            
            if epath == []:
                results = generate_mmo_aggressive_path(seed,research,nbpaths,bonus_spawns,true_spawns,
                                                                 encounters,encsum,dupestore,chained,True,rolls_override)
            elif epath[0] < spawn_remain:
                epath_seed = get_extra_path_seed(seed,epath)
                results = generate_mmo_aggressive_path(epath_seed,research,nbpaths,bonus_spawns,true_spawns,
                                                                 encounters,encsum,dupestore,chained,True,rolls_override)
            else:
                continue
            
            for result in results.values():
                format_bonusround_result(result,path,epath,group_id,map_name,coords,true_spawns,max_spawns,chained)
            
            outbreaks[f"Bonus{path_num} {path} {ext_num} {epath}"] = results

    return outbreaks

# The functions that read MMOs
def get_all_map_mmos(reader, research, inmap, rolls_override = None):
    """reads all mmos on the map"""
    results = {}
    starttime = datetime.now()
    print(f"Starting at {starttime}")

    for map_index in range(MAX_MAPS):
        map_name = get_map_name(reader, map_index)
        if map_name is not None:
            print(f"Map {map_name} starting now...")
            results[map_name] = get_map_mmos(reader, map_index, research, inmap, rolls_override)
            print(f"Map {map_name} complete!")

    endtime = datetime.now()
    print(f"Task done at {endtime}, Took {endtime - starttime}")
    return results

def get_map_mmos(reader, map_index, research, inmap, rolls_override = None, map_name = None):
    """reads a single map's MMOs"""
    outbreaks = {}

    if map_name is None:
        map_name = get_map_name(reader, map_index)

    for group_id in range(MAX_MMOS):
        firstround, bonusround = get_mmo(reader, map_index, group_id, research, inmap, rolls_override, map_name)
        has_bonus = bonusround is not None

        if firstround is not None:
            outbreaks[f"{group_id} {has_bonus}"] = firstround
        if bonusround is not None:
            outbreaks[f"{group_id} {has_bonus} bonus"] = bonusround
            
    return outbreaks

def get_mmo(reader, map_index, group_id, research, inmap, rolls_override = None, map_name = None):
    mmoinfo = get_mmo_info(reader, map_index, group_id)

    if mmoinfo['species_index'] == 0:
        return None, None
    print(f"Species Group: {pokedex.entry_by_index(mmoinfo['species_index']).display_name()}")
    
    if map_name is None:
        map_name = get_map_name(reader, map_index)

    has_bonus = get_encounter_table(mmoinfo['br_encounter'])[0] is not None

    group_seed = get_gen_seed_to_group_seed(reader,group_id) if inmap else mmoinfo['group_seed']
    return mmo_from_seed(group_id, research, group_seed, map_name, mmoinfo['coords'],
                         mmoinfo['fr_encounter'], mmoinfo['br_encounter'], has_bonus,
                         mmoinfo['fr_spawns'], mmoinfo['br_spawns'], rolls_override)
                           
def mmo_from_seed(group_id,research,group_seed,map_name,coords,frencounter,brencounter,has_bonus,max_spawns,br_spawns,rolls_override=None):
    chained = {}

    encounters,encsum = get_encounter_table(frencounter)
    paths = get_nonbonus_paths(max_spawns)
    dupestore = {}
    true_spawns = max_spawns + 3
    firstround = generate_mmo_aggressive_path(group_seed,research,paths,max_spawns,true_spawns,
                                              encounters,encsum,dupestore,chained,False,rolls_override)
    bonusround = None
    
    for result in firstround.values():
        format_firstround_result(result, group_id, map_name, coords, max_spawns, chained)
    
    if has_bonus:
        bonus_spawns = max_spawns + 4
        bonusround_paths = get_bonus_paths(max_spawns)
        encounters,encsum = get_encounter_table(brencounter)
        
        pokemon, alpha = get_species(encounters, 1)
        print(f"Bonus Round Species: {'Alpha ' if alpha else ''}{pokemon.display_name()}")

        bonusround = get_bonusround(bonusround_paths,group_id,research,group_seed,map_name,coords,br_spawns,bonus_spawns,max_spawns,encounters,encsum,chained,rolls_override)
        print(f"Group {group_id} Bonus Complete!")

    print(f"Group {group_id} Complete!")
    return firstround, bonusround

def check_mmo_from_seed(group_seed,research,frencounter,brencounter,has_bonus=False,max_spawns=10,br_spawns=7,rolls_override=None):
    #pylint: disable=too-many-branches,too-many-locals,too-many-arguments
    """reads a single map's MMOs"""
    if len(frencounter) == 0:
        frencounter = "7FA3A1DE69BD271E"
    if len(brencounter) == 0:
        brencounter = "441828854CD36F44"
    
    group_id = 0
    map_name = "From Seed"
    coords = {}

    outbreaks = {}
    firstround, bonusround = mmo_from_seed(group_id,research,group_seed,map_name,coords,frencounter,brencounter,has_bonus,max_spawns,br_spawns,rolls_override)
    has_bonus = bonusround is not None

    if firstround is not None:
        outbreaks[f"0 {has_bonus}"] = firstround
    if bonusround is not None:
        outbreaks[f"0 {has_bonus} bonus"] = bonusround

    return outbreaks
    