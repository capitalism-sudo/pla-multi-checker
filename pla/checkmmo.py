import json
import struct
from datetime import datetime
from app import RESOURCE_PATH
from pla.core import generate_from_seed
from pla.core.util import get_path_display, get_sprite, get_gender_string
from pla.data import SPECIES, NATURES, is_fixed_gender, get_basespecies_form
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

def generate_mmo_aggressive_path(group_seed,rolls,paths,max_spawns,true_spawns,
                                           encounters,encsum,dupestore,chained,isbonus=False):
    """Generate all the pokemon of an outbreak based on a provided aggressive path"""
    # pylint: disable=too-many-locals, too-many-arguments
    # the generation is unique to each path, no use in splitting this function
    storage = {}
    uniques = set()
    true_seed = group_seed
    for i, steps in enumerate(paths):
        main_rng = XOROSHIRO(true_seed)
        for init_spawn in range(1,5):
            generator_seed = main_rng.next()
            main_rng.next() # spawner 1's seed, unused
            fixed_rng = XOROSHIRO(generator_seed)
            encounter_slot = (fixed_rng.next() / (2**64)) * encsum
            species,alpha,nomodspecies = get_species(encounters, encounter_slot)
            fixed_gender = is_fixed_gender(nomodspecies)
            guaranteed_ivs = get_guaranteed_ivs(alpha, isbonus)
            fixed_seed = fixed_rng.next()
            
            if not fixed_seed in uniques:
                uniques.add(fixed_seed)
                path_id = get_path_id(fixed_seed, init_spawn, i, steps)
                dupestore[str(fixed_seed)] = path_id

                ec,pid,ivs,ability,gender,nature,shiny,square = \
                    generate_from_seed(fixed_seed, rolls, guaranteed_ivs, fixed_gender)

                storage[path_id] = {
                    "index": f"<span class='pla-results-init'>Initial Spawn {init_spawn} </span></span>",
                    "generator_seed": f"{generator_seed:X}",
                    "species": species,
                    "shiny": shiny,
                    "square": square,
                    "alpha": alpha,
                    "ec": ec,
                    "pid": pid,
                    "ivs": ivs,
                    "ability": ability,
                    "nature": NATURES[nature],
                    "gender": gender,
                    "rolls": rolls,
                    "dupes": [],
                    "chains": [],
                    "defaultroute": not isbonus,
                    "multi": False
                }
        
        group_seed = main_rng.next()
        respawn_rng = XOROSHIRO(group_seed)

        for step_i,step in enumerate(steps):
            for pokemon in range(1,step+1):
                generator_seed = respawn_rng.next()
                respawn_rng.next() # spawner 1's seed, unused
                fixed_rng = XOROSHIRO(generator_seed)
                encounter_slot = (fixed_rng.next() / (2**64)) * encsum
                species,alpha,nomodspecies = get_species(encounters,encounter_slot)
                fixed_gender = is_fixed_gender(nomodspecies)
                guaranteed_ivs = get_guaranteed_ivs(alpha, isbonus)
                fixed_seed = fixed_rng.next()
                    
                #if not fixed_seed in uniques and (sum(steps[:step_i]) + pokemon + 4) <= true_spawns:
                if not fixed_seed in uniques:
                    uniques.add(fixed_seed)
                    path_id = get_path_id(fixed_seed, steps[:step_i] + [pokemon], i, steps)
                    dupestore[str(fixed_seed)] = path_id

                    ec,pid,ivs,ability,gender,nature,shiny,square = \
                        generate_from_seed(fixed_seed, rolls, guaranteed_ivs, fixed_gender)

                    storage[path_id] = {
                        "index": get_index_string(steps[:step_i], pokemon),
                        "generator_seed": f"{generator_seed:X}",
                        "species": species,
                        "shiny": shiny,
                        "square": square,
                        "alpha": alpha,
                        "ec": ec,
                        "pid": pid,
                        "ivs": ivs,
                        "ability": ability,
                        "nature":NATURES[nature],
                        "gender":gender,
                        "rolls":rolls,
                        "dupes": [],
                        "chains": [],
                        "defaultroute": not isbonus and sum(steps[:step_i]) == len(steps[:step_i]) and pokemon == 1,
                        "multi":False
                    }
                else:
                    path_str = get_storage_pathstring(steps[:step_i], step)
                    if path_str not in storage[dupestore[str(fixed_seed)]] \
                       and path_str != get_storage_pathstring(steps[:step_i], pokemon) \
                       and (step+1) - pokemon < 3:
                        #print(f" Step+1 = {step+1}, Pokemon = {pokemon}")
                        respawns = true_spawns - 4
                        ghosts = (sum(steps[:step_i])+pokemon) - respawns
                        dupestring = get_dupestring(steps)
                        #storage[str(dupestore[str(fixed_seed)])]["dupes"].append(f"Path: {'|'.join(str(s) for s in steps)}")
                        if ghosts <= 0:
                            storage[dupestore[str(fixed_seed)]]["dupes"].append(dupestring)
                    #print(f"Duplicate found at {fixed_seed}: {storage[str(dupestore[str(fixed_seed)])]['dupes']}")
            respawn_rng = XOROSHIRO(respawn_rng.next())
    return storage

def get_path_id(seed, spawn, i, steps):
    return f"{seed} + {spawn} + {i} + {steps}"

def get_storage_pathstring(steps, final):
    return f"Path: {'|'.join(str(s) for s in steps + [final])}"

def get_guaranteed_ivs(alpha, isbonus):
    if isbonus and alpha:
        return 4
    if isbonus or alpha:
        return 3
    return 0

def get_index_string(current_step, respawn_index):
    return "Path: " + ''.join(f" D{s}, " for s in current_step) + f" D{respawn_index}"

def get_dupestring(steps):
    return " Path: " + ''.join(f" D{step}, " for step in steps)

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

    return "", False

def get_encounter_table(enc_pointer):
    if enc_pointer not in encmap:
        return None, 0
    
    encounters = encmap[enc_pointer]
    encsum = sum(e['slot'] for e in encounters)
    return encounters, encsum

def get_encounter_pointer(reader, group_id, map_index, bonus):
    offset = 0x2c if bonus else 0x24
    enc_pointer = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                              f"{0x1d4 + 0x90*group_id + 0xb80*map_index + offset:X}", 8)
    return f"0x{enc_pointer:X}"

def get_group_seed(reader, group_id, map_index):
    return reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                         f"{0x1d4 + 0x90*group_id + 0xb80*map_index + 0x44:X}", 8)

def get_gen_seed_to_group_seed(reader,group_id):
    gen_seed = reader.read_pointer_int(f"[[[[[[main+42EEEE8]+78]+" \
                                       f"{0xD48 + 0x8*group_id:X}]+58]+38]+478]+20", 8)
    return (gen_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF

def get_max_spawns(reader, group_id, map_index, isbonus):
    offset = 0x60 if isbonus else 0x4c
    return reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                             f"{0x1d4 + 0x90*group_id + 0xb80*map_index + offset:X}", 4)

def get_map_name(reader, map_index):
    map_id = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                     f"{0x1d4 + 0xb80*map_index - 0x24:X}", 2)
    return mapnamevals.get(f"{map_id:X}", "None")

def get_all_map_names(reader):
    """gets all map names"""
    return [get_map_name(reader, map_index) for map_index in range(MAX_MAPS)]

def get_bonus_flag(reader, group_id, map_index):
    return reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                   f"{0x1d4 + 0x90*group_id + 0xb80*map_index + 0x18:X}", 1) == 1

def get_firstround_paths(max_spawns):
    return nonbonuspaths[str(max_spawns)]

def get_bonusround_paths(max_spawns):
    return allpaths[str(max_spawns)]

def get_group_coordinates(reader, group_id, map_index):
    """reads coordinates of mmo group"""
    coords = struct.unpack('fff', reader.read_pointer(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                                      f"{0x1d4 + 0x90*group_id + 0xb80*map_index - 0x14:X}", 12))
    coordinates = {
        "x":coords[0],
        "y":coords[1],
        "z":coords[2]
    }
    return coordinates

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

    basespecies, form = get_basespecies_form(result["species"])
    result["sprite"] = get_sprite(basespecies, form, result["shiny"])
    result["gender"] = get_gender_string(basespecies, result["gender"])
    
    if result["shiny"]:
        chained[result["index"]] = f"<span class='pla-results-firstpath'>First Round </span>{result['index']}"
        print(f"Chained: {chained}")

def format_bonusround_result(result,path,epath,group_id,map_name,coords,true_spawns,max_spawns,chained):
    result["index"] = get_path_display(result["index"], path, epath)
    for du,dupe in enumerate(result["dupes"]):
        result["dupes"][du] = f"Bonus {result['dupes'][du]} "
    result["group"] = group_id
    result["mapname"] = map_name
    result["coords"] = coords
    result["numspawns"] = max_spawns
            
    cutspecies, form = get_basespecies_form(result["species"])
    result["sprite"] = get_sprite(cutspecies, form, result["shiny"])
    result["gender"] = get_gender_string(cutspecies, result["gender"])

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

    if len(path) == sum(path):
        result["defaultroute"] = True
    else:
        result["defaultroute"] = False

def get_bonusround(paths,group_id,rolls,group_seed,map_name,coords,
                    true_spawns,bonus_spawns,max_spawns,encounters,encsum,chained):
    #pylint: disable=too-many-branches
    """reads info about a bonus path"""
    isbonus = True
    outbreaks = {}
    dupestore = {}
    nbpaths = nonbonuspaths[str(true_spawns)]

    for path_num, path in enumerate(paths):
        seed = get_bonus_seed(group_seed,path)
        
        for ext,epath in enumerate(extrapaths):
            spawn_remain = max_spawns - sum(path)
            
            if epath == []:
                results = generate_mmo_aggressive_path(seed,rolls,nbpaths,bonus_spawns,true_spawns,
                                                                 encounters,encsum,dupestore,chained,isbonus)
            elif epath[0] < spawn_remain:
                epath_seed = get_extra_path_seed(seed,epath)
                results = generate_mmo_aggressive_path(epath_seed,rolls,nbpaths,bonus_spawns,true_spawns,
                                                                 encounters,encsum,dupestore,chained,isbonus)
            else:
                continue
            
            for index in results:
                format_bonusround_result(results[index],path,epath,group_id,map_name,coords,true_spawns,max_spawns,chained)
            
            outbreaks[f"Bonus{path_num} {path} {ext} {epath}"] = results

    return outbreaks

# The functions that read MMOs
def get_all_map_mmos(reader, rolls, inmap):
    """reads all mmos on the map"""
    results = {}
    starttime = datetime.now()
    print(f"Starting at {starttime}")

    for map_index in range(MAX_MAPS):
        map_name = get_map_name(reader, map_index)
        if map_name != "None":
            print(f"Map {map_name} starting now...")
            results[map_name] = get_map_mmos(reader, map_index, rolls, inmap)
            print(f"Map {map_name} complete!")

    endtime = datetime.now()
    print(f"Task done at {endtime}, Took {endtime - starttime}")
    return results

def get_map_mmos(reader, map_index, rolls, inmap):
    #pylint: disable=too-many-branches,too-many-locals,too-many-arguments
    """reads a single map's MMOs"""
    outbreaks = {}
    print(f"Rolls: {rolls}")
    for group_id in range(MAX_MMOS):
        firstround, bonusround = get_mmo(reader, group_id, map_index, rolls, inmap)
        has_bonus = bonusround is not None

        if firstround is not None:
            outbreaks[f"{group_id} {has_bonus}"] = firstround
        if bonusround is not None:
            outbreaks[f"{group_id} {has_bonus} bonus"] = bonusround
            
    return outbreaks

def get_mmo(reader, group_id, map_index, rolls, inmap):
    species_num = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4 + 0x90*group_id + 0xb80*map_index:X}", 2)
    if species_num == 0:
        return None, None
    
    map_name = get_map_name(reader, map_index)
    
    print(f"Species Group: {SPECIES[species_num]}")
    frencounter = get_encounter_pointer(reader,group_id,map_index,False)
    
    brencounter = get_encounter_pointer(reader,group_id,map_index,True)
    bonus_enctable,_ = get_encounter_table(brencounter)
    has_bonus = bonus_enctable is not None
    br_spawns = get_max_spawns(reader,group_id,map_index,True)
    
    coords = get_group_coordinates(reader,group_id,map_index)
    group_seed = get_gen_seed_to_group_seed(reader,group_id) if inmap else get_group_seed(reader,group_id,map_index)
    max_spawns = get_max_spawns(reader,group_id,map_index,False)

    return mmo_from_seed(group_id,rolls,group_seed,map_name,coords,frencounter,brencounter,has_bonus,max_spawns,br_spawns)
                           
def mmo_from_seed(group_id,rolls,group_seed,map_name,coords,frencounter,brencounter,has_bonus,max_spawns,br_spawns):
    chained = {}

    encounters,encsum = get_encounter_table(frencounter)
    paths = get_firstround_paths(max_spawns)
    dupestore = {}
    true_spawns = max_spawns + 3
    firstround = generate_mmo_aggressive_path(group_seed,rolls,paths,max_spawns,true_spawns,
                                                        encounters,encsum,dupestore,chained,False)
    bonusround = None
    
    for index in firstround:
        if index not in ('index','description'):
            format_firstround_result(firstround[str(index)],group_id,map_name,coords,max_spawns,chained)
    
    if has_bonus:
        bonus_spawns = max_spawns + 4
        bonusround_paths = get_bonusround_paths(max_spawns)
        encounters,encsum = get_encounter_table(brencounter)
        
        species,_,_ = get_species(encounters,1)
        print(f"Bonus Round Species: {species}")

        bonusround = get_bonusround(bonusround_paths,group_id,rolls,group_seed,map_name,coords,br_spawns,bonus_spawns,max_spawns,encounters,encsum,chained)
        print(f"Group {group_id} Bonus Complete!")

    print(f"Group {group_id} Complete!")
    return firstround, bonusround

def check_mmo_from_seed(group_seed,rolls,frencounter,brencounter,has_bonus=False,max_spawns=10,br_spawns=7):
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
    firstround, bonusround = mmo_from_seed(group_id,rolls,group_seed,map_name,coords,frencounter,brencounter,has_bonus,max_spawns,br_spawns)
    has_bonus = bonusround is not None

    if firstround is not None:
        outbreaks[f"0 {has_bonus}"] = firstround
    if bonusround is not None:
        outbreaks[f"0 {has_bonus} bonus"] = bonusround

    return outbreaks
    