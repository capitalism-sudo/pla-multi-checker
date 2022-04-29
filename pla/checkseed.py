import random
from datetime import datetime

from pla.core import generate_from_seed
from pla.core.util import get_path_display, get_sprite, get_gender_string
from pla.data import NATURES, is_fixed_gender, get_basespecies_form
from pla.rng import XOROSHIRO
# common mmo functionality
from pla.checkmmo import encmap, allpaths, nonbonuspaths, extrapaths, initchain, get_bonus_seed, get_extra_path_seed, get_guaranteed_ivs, get_index_string, get_species

# Any reason for this not to use the same algorithm as in checkmmo.py?
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
            set_gender = is_fixed_gender(nomodspecies)
            guaranteed_ivs = get_guaranteed_ivs(alpha, isbonus)
            fixed_seed = fixed_rng.next()
            ec,pid,ivs,ability,gender,nature,shiny,square = \
                generate_from_seed(fixed_seed,rolls,guaranteed_ivs,set_gender)
            
            if not fixed_seed in uniques:
                uniques.add(fixed_seed)
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
                    "chains":[],
                    "multi": False
                    }
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
                set_gender = is_fixed_gender(nomodspecies)
                guaranteed_ivs = get_guaranteed_ivs(alpha, isbonus)
                fixed_seed = fixed_rng.next()
                ec,pid,ivs,ability,gender,nature,shiny,square = \
                    generate_from_seed(fixed_seed,rolls,guaranteed_ivs,set_gender)
                if not fixed_seed in uniques:
                    uniques.add(fixed_seed)
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
                        "chains":[],
                        "multi":False
                    }
                    if not isbonus and sum(steps[:step_i]) == len(steps[:step_i]) and pokemon == 1:
                        info["defaultroute"] = True
                    else:
                        info["defaultroute"] = False
                   # print(info)
                    storage[f"{fixed_seed} + {steps[:step_i] + [pokemon]} " \
                            f"+ {random.randint(0,100)} + {i} + {steps}"]=info
            respawn_rng = XOROSHIRO(respawn_rng.next())
    return storage

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

def read_bonus_pathinfo(paths,rolls,group_seed,map_name,
                        true_spawns,bonus_spawns,max_spawns,encounter,chained):
    #pylint: disable=too-many-branches
    """reads info about a bonus path"""
    isbonus = True
    outbreaks = {}
    nbpaths = nonbonuspaths[str(true_spawns)]
    for tex,value in enumerate(paths):
        seed = get_bonus_seed(group_seed,value)
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
                display[index]["index"] = get_path_display(display[index]["index"], value, extra, epath)
                display[index]["group"] = 0
                display[index]["mapname"] = map_name
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
                            print(f"frpath: {frpath}")
                            print(f"frbonuspath: {frbonuspath}")
                            if len(frpath) <= len(frbonuspath):
                                remain = max_spawns - 4
                                match = True
                                for v in range(0,len(frpath)-1):
                                    remain = remain - frpath[v]
                                    if frpath[v] != frbonuspath[v]:
                                        match = False
                                if match:
                                    if len(frpath) == len(frbonuspath) and frpath[len(frpath)-1] == frbonuspath[len(frbonuspath)-1]:
                                        print(f"Exact first round path, adding frpath {frpath} and frbonuspath {frbonuspath}")
                                        display[index]["chains"].append(chained[chain])
                                    elif frbonuspath[len(frpath)-1] >= frpath[len(frpath)-1]:
                                        difference = frbonuspath[len(frpath)-1] - frpath[len(frpath)-1]
                                        print(f"Difference: {difference} Remain: {remain}")
                                        if difference < remain or difference == 0:
                                            print("Bonus Path > frpath, adding")
                                            display[index]["chains"].append(chained[chain])
                    if chained.get(chainstring, None) is not None:
                        chainresult.append(chainstring)
                    for ini,initcha in enumerate(initchain):
                        if chained.get(initcha, None) is not None:
                            chainresult.append(initcha)
                    #print(chained)
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
                            print(chained[res])
                            print("Possible Chain Shiny Found!")
                            bonuscheck = chained[res].rpartition("Bonus Round Path:")[2].replace(" ",'').replace("D",'').split(',')
                            print(f"Bonus Check: {bonuscheck}")
                            currcheck = display[index]["index"].rpartition("Bonus Round Path:")[2].replace(" ",'').replace("D",'').split(',')
                            print(f"Curr Check: {currcheck}")
                            #print(f"Initial in? {'Initial' in bonuscheck[len(bonuscheck)-1]}")
                            if "Initial" in bonuscheck[len(bonuscheck)-1] or "FirstRound" in bonuscheck[0] or (len(bonuscheck) < len(currcheck) and bonuscheck[0] == currcheck[0]):
                                print("Either an initial spawn, or bonuscheck < currcheck and they're on the same path, adding.")
                                display[index]["chains"].append(chained[res])
                            elif len(bonuscheck) < len(currcheck):
                                bonuscheck = list(map(int, bonuscheck))
                                currcheck = list(map(int, currcheck))
                                respawns = true_spawns - 4
                                remain = respawns
                                for t in range(0,len(bonuscheck)):
                                    remain = remain - bonuscheck[t]
                                if remain >= 1:
                                    print("Remaining >1, adding")
                                    display[index]["chains"].append(chained[res])
                            elif len(bonuscheck) <= len(currcheck) and (len(currcheck) > 1 and (bonuscheck[0] == currcheck[0]) or ((len(bonuscheck) == len(currcheck) and bonuscheck[0] == currcheck[0]))):
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
                                    for z in range(0,len(currcheck)-1):
                                        pokesleft = pokesleft - currcheck[z]
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
                                         
def check_from_seed(group_seed,rolls,frencounter,brencounter,bonus_flag=False,max_spawns=10,br_spawns=7):
    #pylint: disable=too-many-branches,too-many-locals,too-many-arguments
    """reads a single map's MMOs"""
    if len(frencounter) == 0:
        frencounter = "7FA3A1DE69BD271E"
    if len(brencounter) == 0:
        brencounter = "441828854CD36F44"
    i = 0
    chained = {}
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
            str_index = str(index)
            display[str_index]["group"] = 0
            display[str_index]["numspawns"] = max_spawns

            cutspecies, form = get_basespecies_form(display[str_index]["species"])
            display[str_index]["sprite"] = get_sprite(cutspecies, form, display[str_index]["shiny"])
            display[str_index]["gender"] = get_gender_string(cutspecies, display[str_index]["gender"])
            if display[str_index]["shiny"]:
                chained[display[str_index]["index"]] = f"<span class='pla-results-firstpath'>First Round </span>{display[str_index]['index']}"
                print(f"Chiained: {chained}")
    outbreaks[f"{i} {bonus_flag}"] = display

    if bonus_flag:
        true_spawns = max_spawns
        bonus_spawns = true_spawns + 4
        bonus_seed = allpaths[str(max_spawns)]
        true_spawns = br_spawns
        result = read_bonus_pathinfo(bonus_seed,rolls,group_seed,map_name,true_spawns,bonus_spawns,max_spawns,brencounter,chained)
        outbreaks[f"{i} {bonus_flag}bonus"] = result
        print(f"Group {i} Bonus Complete!")

    print(f"Group {i} Complete!")        

    return outbreaks
