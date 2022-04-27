import json
import struct
from datetime import datetime
from app import RESOURCE_PATH
from pla.core import generate_from_seed
from pla.core.util import get_path_display, get_sprite, get_gender_string
from pla.data import SPECIES, NATURES, is_fixed_gender, get_basespecies_form
from pla.rng import XOROSHIRO

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

def generate_mass_outbreak_aggressive_path(group_seed,rolls,paths,spawns,true_spawns,
                                           encounters,encsum,dupestore,chained,isbonus=False,isalpha=False):
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
            species,alpha,nomodspecies = get_species(encounters,encounter_slot)
            set_gender = is_fixed_gender(nomodspecies)
            guaranteed_ivs = get_guaranteed_ivs(alpha, isbonus)
            fixed_seed = fixed_rng.next()
            ec,pid,ivs,ability,gender,nature,shiny,square = \
                generate_from_seed(fixed_seed,rolls,guaranteed_ivs,set_gender)
            if not fixed_seed in uniques:
                uniques.add(fixed_seed)
                dupestore[str(fixed_seed)] = f"{fixed_seed} + {init_spawn} + " \
                        f"+ {i} + {steps}"
                info = {
                    "index":f"<span class='pla-results-init'>Initial Spawn " \
                    f"{init_spawn} </span></span>",
                    "spawn":True,
                    "generator_seed":f"{generator_seed:X}",
                    "species":species,
                    "shiny":shiny,
                    "square": square,
                    "alpha":alpha,
                    "ec":ec,
                    "pid":pid,
                    "ivs":ivs,
                    "ability":ability,
                    "nature":NATURES[nature],
                    "gender":gender,
                    "rolls":rolls,
                    "dupes": [],
                    "chains": [],
                    "multi":False
                }
                if not fixed_seed in uniques:
                    info["unique"] = True
                    uniques.add(fixed_seed)
                else:
                    info["unique"] = False
                if not isbonus:
                    info["defaultroute"] = True
                else:
                    info["defaultroute"] = False
                #print(info)
                storage[f"{fixed_seed} + {init_spawn} + " \
                        f"+ {i} + {steps}"]=info
        group_seed = main_rng.next()
        respawn_rng = XOROSHIRO(group_seed)
        for step_i,step in enumerate(steps):
            for pokemon in range(1,step+1):
                generator_seed = respawn_rng.next()
                respawn_rng.next() # spawner 1's seed, unused
                fixed_rng = XOROSHIRO(generator_seed)
                encounter_slot = (fixed_rng.next() / (2**64)) * encsum
                species,alpha,nomodspecies = get_species(encounters,encounter_slot)
                set_gender = is_fixed_gender(nomodspecies)
                guaranteed_ivs = get_guaranteed_ivs(alpha, isbonus)
                fixed_seed = fixed_rng.next()
                ec,pid,ivs,ability,gender,nature,shiny,square = \
                    generate_from_seed(fixed_seed,rolls,guaranteed_ivs,set_gender)
                    
                #if not fixed_seed in uniques and (sum(steps[:step_i]) + pokemon + 4) <= true_spawns:
                if not fixed_seed in uniques:
                    uniques.add(fixed_seed)
                    dupestore[str(fixed_seed)] = f"{fixed_seed} + {steps[:step_i] + [pokemon]} " \
                            f"+ {i} + {steps}"
                    info = {
                        #"index":f"Path: {'|'.join(str(s) for s in steps[:step_i] + [pokemon])} </span>",
                        "index": get_index_string(steps[:step_i], pokemon),
                        "spawn":True,
                        "generator_seed":f"{generator_seed:X}",
                        "species":species,
                        "shiny":shiny,
                        "square":square,
                        "alpha":alpha,
                        "ec":ec,
                        "pid":pid,
                        "ivs":ivs,
                        "ability":ability,
                        "nature":NATURES[nature],
                        "gender":gender,
                        "rolls":rolls,
                        "dupes": [],
                        "chains": [],
                        "multi":False
                    }
                    if not fixed_seed in uniques:
                        uniques.add(fixed_seed)
                        info["unique"] = True
                    else:
                        info["unique"] = False
                    if not isbonus and sum(steps[:step_i]) == len(steps[:step_i]) and pokemon == 1:
                        info["defaultroute"] = True
                    else:
                        info["defaultroute"] = False
                   # print(info)
                    storage[f"{fixed_seed} + {steps[:step_i] + [pokemon]} " \
                            f"+ {i} + {steps}"]=info
                else:
                    if f"Path: {'|'.join(str(s) for s in steps[:step_i] + [step])}" not in storage[str(dupestore[str(fixed_seed)])] \
                       and f":Path: {'|'.join(str(s) for s in steps[:step_i] + [step])}" != f"Path: {'|'.join(str(s) for s in steps[:step_i] + [pokemon])}" \
                       and (step+1) - pokemon < 3:
                        #print(f" Step+1 = {step+1}, Pokemon = {pokemon}")
                        respawns = true_spawns - 4
                        ghosts = (sum(steps[:step_i])+pokemon) - respawns
                        dupestring = get_dupestring(steps)
                        #storage[str(dupestore[str(fixed_seed)])]["dupes"].append(f"Path: {'|'.join(str(s) for s in steps)}")
                        if ghosts <= 0:
                            storage[str(dupestore[str(fixed_seed)])]["dupes"].append(dupestring)
                    #print(f"Duplicate found at {fixed_seed}: {storage[str(dupestore[str(fixed_seed)])]['dupes']}")
            respawn_rng = XOROSHIRO(respawn_rng.next())
    return storage

def get_guaranteed_ivs(alpha, isbonus):
    if isbonus and alpha:
        return 4
    if isbonus or alpha:
        return 3
    return 0

def get_index_string(current_step, pokemon_index):
    string = "Path: "
    for s in current_step:
        string = string + f" D{s}, "
    string = string + f"D{pokemon_index}"

def get_dupestring(steps):
    dupestring = " Path: "
    for s,st in enumerate(steps):
        #print(f"Steps: {steps}")
        #print(f"S: {s}, St: {st}")
        dupestring = dupestring + f" D{st}, "
    #print(f"Dupestring: {dupestring}")
    return dupestring

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
    bonus_seed = (respawn_rng.next() - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF
    return bonus_seed

def read_mass_outbreak_rng(reader,group_id,rolls,mapcount,chained,species,group_seed,max_spawns,bonus_flag):
    if species == 201:
        rolls = 19
    print(f"Species Group: {SPECIES[species]}")
    encounters,encsum = get_encounter_table(reader,group_id,mapcount,bonus_flag)
    paths = nonbonuspaths[str(max_spawns)]
    dupestore = {}

    true_spawns = max_spawns
    if bonus_flag:
        max_spawns = 10
    else:
        max_spawns += 3
    display = generate_mass_outbreak_aggressive_path(group_seed,rolls,paths,max_spawns,
                                                     true_spawns,encounters,encsum,dupestore,chained,bonus_flag,False)
    return display

def get_encounter_table(reader,group_id,mapcount,bonus):
    encounters = {}
    encsum = 0
    if bonus:
        enc_pointer = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                              f"{0x1d4+group_id*0x90 + 0xb80 * mapcount+0x2c:X}",8)
    else:
        enc_pointer = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                              f"{0x1d4+group_id*0x90 + 0xb80 * mapcount+0x24:X}",8)

    enc_pointer = f"0x{enc_pointer:X}"

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

def generate_mass_outbreak_aggressive_path_normal(group_seed,rolls,steps,uniques,paths,storage):
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
        ec,pid,ivs,ability,gender,nature,shiny,square = \
            generate_from_seed(fixed_seed,rolls,3 if alpha else 0)
        if not fixed_seed in uniques:
            uniques.add(fixed_seed)
            info = {
                "index":f"Initial Spawn {init_spawn}</span>",
                "spawn":True,
                "generator_seed":f"{generator_seed:X}",
                "shiny":shiny,
                "square": square,
                "alpha":alpha,
                "ec":ec,
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
            ec,pid,ivs,ability,gender,nature,shiny,square = \
                generate_from_seed(fixed_seed,rolls,3 if alpha else 0)
            if not fixed_seed in uniques:
                uniques.add(fixed_seed)
                info = {
                    "index":f"Path: {'|'.join(str(s) for s in steps[:step_i] + [pokemon])}</span>",
                    "spawn":True,
                    "generator_seed":f"{generator_seed:X}",
                    "shiny":shiny,
                    "square": square,
                    "alpha":alpha,
                    "ec":ec,
                    "pid":pid,
                    "ivs":ivs,
                    "ability":ability,
                    "nature":NATURES[nature],
                    "gender":gender
                }
                paths.append(f"{'|'.join(str(s) for s in steps[:step_i] + [pokemon])}")
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
                                 paths=None,
                                 storage=None):
    """Recursively pathfind to possible shinies for the current outbreak via multi battles"""
    # pylint: disable=too-many-arguments
    # can this algo be improved?
    if steps is None or uniques is None or storage is None or paths is None:
        steps = []
        uniques = set()
        storage = {}
        paths = []
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
                                            paths,
                                            storage) is not None:
                return storage,paths
    else:
        _steps.append(spawns - sum(_steps) - 4)
        generate_mass_outbreak_aggressive_path_normal(group_seed,rolls,_steps,uniques,paths,storage)
        if _steps == get_final_normal(spawns):
            return storage,paths
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
        result,paths = aggressive_outbreak_pathfind_normal(group_seed, rolls, spawns)
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
        return info,paths
    else:
        return info,paths

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
    
    max_spawns = reader.read_pointer_int(f"[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                         f"{0x20 + group_id*0x50+0x40:X}",8)

    coords = struct.unpack('fff',reader.read_pointer(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                                     f"{0x20 + group_id*0x50+0x20:X}",12))

    coordinates = {
        "x":coords[0],
        "y":coords[1],
        "z":coords[2]
    }

    return species,group_seed,max_spawns,coordinates

def read_bonus_pathinfo(reader,paths,group_id,mapcount,rolls,group_seed,map_name,
                        coords,true_spawns,bonus_spawns,max_spawns,species,chained):
    #pylint: disable=too-many-branches
    """reads info about a bonus path"""
    isbonus = True
    outbreaks = {}
    dupestore = {}
    nbpaths = nonbonuspaths[str(true_spawns)]
    for tex,value in enumerate(paths):
        seed = get_bonus_seed(group_seed,value)
        extra = [1] * (max_spawns - sum(value))
        encounters,encsum = get_encounter_table(reader,group_id,mapcount,True)
        for ext,epath in enumerate(extrapaths):
            spawn_remain = max_spawns - sum(value)
            if epath == []:
                display = generate_mass_outbreak_aggressive_path(seed,rolls,nbpaths,
                                                                 bonus_spawns,
                                                                 true_spawns,encounters,
                                                                 encsum,dupestore,chained,isbonus,False)
            elif epath[0] < spawn_remain:
                epath_seed = get_extra_path_seed(seed,epath)
                display = generate_mass_outbreak_aggressive_path(epath_seed,rolls,
                                                                 nbpaths,bonus_spawns,true_spawns,
                                                                 encounters,encsum,dupestore,chained,isbonus,False)
            else:
                continue
            
            for index in display:
                display[index]["index"] = get_path_display(display[index]["index"], value, epath)
                for du,dupe in enumerate(display[index]["dupes"]):
                    display[index]["dupes"][du] = f"Bonus {display[index]['dupes'][du]} "
                display[index]["group"] = group_id
                display[index]["mapname"] = map_name
                display[index]["coords"] = coords
                display[index]["numspawns"] = max_spawns
                        
                cutspecies, form = get_basespecies_form(display[index]["species"])
                display[index]["sprite"] = get_sprite(cutspecies, form, display[index]["shiny"])
                display[index]["gender"] = get_gender_string(cutspecies, display[index]["gender"])

                if display[index]["shiny"]:
                    chainstring = display[index]["index"].rpartition("Bonus")[0]
                    chainresult = []
                    frchainstring = display[index]["index"].split('+')[0]
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
                                        display[index]["chains"].append(chained[chain])
                                    elif frbonuspath[len(frpath)-1] >= frpath[len(frpath)-1]:
                                        difference = frbonuspath[len(frpath)-1] - frpath[len(frpath)-1]
                                        if remain > difference or difference == 0:
                                            print("Bonus Path > frpath, adding")
                                            display[index]["chains"].append(chained[chain])
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
                            currcheck = display[index]["index"].rpartition("Bonus Path:")[2].replace(" ",'').replace("D",'').split(',')
                            print(f"Curr Check: {currcheck}")
                            #print(f"Initial in? {'Initial' in bonuscheck[len(bonuscheck)-1]}")
                            if "Initial" in bonuscheck[len(bonuscheck)-1] or "FirstRound" in bonuscheck[0] or (len(bonuscheck) < len(currcheck) and bonuscheck[0] == currcheck[0]):
                                print("Either an initial spawn, or bonuscheck < currcheck and they're on the same path, adding.")
                                display[index]["chains"].append(chained[res])
                            elif len(bonuscheck) <= len(currcheck) and (len(currcheck) > 1 and bonuscheck[0] == currcheck[0]):
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
                                    display[index]["chains"].append(chained[res])
                                else:
                                    pokesleft = respawns
                                    for i in range(0,len(currcheck)-1):
                                        pokesleft = pokesleft - currcheck[i]
                                    print(f"Amount left: {pokesleft}")
                                    if (pokesleft <= 0) and not difference >= 2:
                                        print(f"Pokesleft <=0 and Difference < 2, adding")
                                        display[index]["chains"].append(chained[res])
                                    elif pokesleft > 1 and difference < pokesleft:
                                        print(f"Pokesleft >0 and difference = {difference}, adding")
                                        display[index]["chains"].append(chained[res])
                                    else:
                                        print(f"Pokesleft not <=0 or difference >= 2.")
                    chained[display[index]["index"].rpartition("Bonus")[0]] = display[index]["index"]

                if len(value) == sum(value):
                    display[index]["defaultroute"] = True
                else:
                    display[index]["defaultroute"] = False

            outbreaks[f"Bonus{tex} {value} {ext} {epath}"] = display

    return outbreaks
                                         
def get_map_mmos(reader,mapcount,rolls,inmap):
    #pylint: disable=too-many-branches,too-many-locals,too-many-arguments
    """reads a single map's MMOs"""
    outbreaks = {}
    print(f"Rolls: {rolls}")
    map_name = get_map_name(reader,mapcount)
    for i in range(0,16):
        chained = {}
        enctable,_ = get_encounter_table(reader,i,mapcount,True)
        bonus_flag = False if enctable is None else True
        coords = read_group_coordinates(reader,i,mapcount)
        species_num = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+{0x1d4+i*0x90 + 0xb80 * mapcount:X}",2)
        if species_num != 0:
            if not inmap:
                group_seed = get_group_seed(reader,i,mapcount)
            else:
                group_seed = get_gen_seed_to_group_seed(reader,i)
            max_spawns = get_max_spawns(reader,i,mapcount,False)
            display = read_mass_outbreak_rng(reader,i,rolls,mapcount,chained,species_num,group_seed,max_spawns,False)
            for index in display:
                if index not in ('index','description'):
                    str_index = str(index)
                    display[str_index]["group"] = i
                    display[str_index]["mapname"] = map_name
                    display[str_index]["coords"] = coords
                    display[str_index]["numspawns"] = max_spawns

                    cutspecies, form = get_basespecies_form(display[str_index]["species"])
                    display[str_index]["sprite"] = get_sprite(cutspecies, form, display[str_index]["shiny"])
                    display[str_index]["gender"] = get_gender_string(cutspecies, display[str_index]["gender"])
                    
                    if display[str_index]["shiny"]:
                        chained[display[str_index]["index"]] = f"<span class='pla-results-firstpath'>First Round </span>{display[str_index]['index']}"
                        print(f"Chiained: {chained}")
            if bonus_flag:
                species,alpha,_ = get_species(enctable,1)
                print(f"Bonus Round Species: {species}")
                true_spawns = max_spawns
                bonus_spawns = true_spawns + 4
                bonus_seed = allpaths[str(max_spawns)]
                true_spawns = get_max_spawns(reader,i,mapcount,True)
                result = read_bonus_pathinfo(reader,bonus_seed,i,mapcount,rolls,group_seed,map_name,coords,true_spawns,bonus_spawns,max_spawns,species_num,chained)
                print(f"Group {i} Bonus Complete!")
            outbreaks[f"{i} " + f"{bonus_flag}"] = display
            print(f"Group {i} Complete!")
            if bonus_flag:
                outbreaks[f"{i} " + f"{bonus_flag}" + "bonus"] = result
            #print(chained)
        else:
            continue
            
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
            display,_ = next_filtered_aggressive_outbreak_pathfind_normal(group_seed,rolls,max_spawns)
            
            if display is None:
                display = []
            
            for index in display:
                if index not in ('index', 'description'):
                    str_index = str(index)
                    display[str_index]["group"] = i
                    display[str_index]["mapname"] = "Normal Outbreak"
                    display[str_index]["numspawns"] = max_spawns
                    if SPECIES[species] == "Basculin":
                        display[str_index]["species"] = "Basculin-2"
                    else:
                        display[str_index]["species"] = SPECIES[species]
                    display[str_index]["coords"] = coordinates

                    cutspecies, form = get_basespecies_form(display[str_index]["species"])
                    display[str_index]["sprite"] = get_sprite(cutspecies, form, display[str_index]["shiny"])
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
