# Go to root of PyNXReader
import signal
import sys
import json
import requests
import colorama
sys.path.append('../../')

from nxreader import NXReader
from rng import XOROSHIRO
from lookups import Util
from colorama import Fore, Back, Style


config = json.load(open("../../config.json"))
reader = NXReader(config["IP"],usb_connection=config["USB"])
colorama.init()

WEATHER = {
    1:"None",
    2:"Sunny",
    3:"Cloudy",
    4:"Rain",
    5:"Snow",
    6:"Drought",
    7:"Fog",
    8:"Rainstorm",
    9:"Snowstorm"
    }
TIME = {
    1:"Dawn",
    2:"Day",
    3:"Dusk",
    4:"Night"
}

def signal_handler(signal, advances): #CTRL+C handler
    print("Stop request")
    reader.close()

signal.signal(signal.SIGINT, signal_handler)

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

def read_wild_rng(group_id,rolls,guaranteed_ivs,encsum,encmin,encmax):
    group_seed = reader.read_pointer_int(f"main+4268ee0]+330]+{0x70+group_id*0x440+0x408:X}",8)
    main_rng = XOROSHIRO(group_seed)
    for adv in range(1,40960):
        rng = XOROSHIRO(*main_rng.seed.copy())
        spawner_seed = rng.next()
        rng = XOROSHIRO(spawner_seed)
        encslot = (rng.next() / (2**64)) * encsum
        fixed_seed = rng.next()
        ec,pid,ivs,ability,gender,nature,shiny = \
            generate_from_seed(fixed_seed,rolls,guaranteed_ivs)
        if shiny:
            if (encslot > encmin and encslot < encmax):
                print("Generator Seed: ",hex(spawner_seed))
                print("Enc Slot Value:",encslot)
                break
        main_rng.next()
        main_rng.next()
        main_rng = XOROSHIRO(main_rng.next())
    return adv,group_seed,fixed_seed,ec,pid,ivs,ability,gender,nature,shiny

def get_spawns_by_category(spawntable):
        for keys in spawntable:
            if "Any Time" in keys:
                if "All Weather" in keys:
                    print(keys)
                    return spawntable[keys]
                else:
                    for weathers in WEATHER:
                        print(f"{weathers}) {WEATHER[weathers]}")
                    encwea = int(input("Weather: "))
                    encsum = "Any Time/" + WEATHER[encwea]
                    print()
                    print("Searching ",encsum)
                    print()
                    return(spawntable[encsum])
            elif "All Weather" in keys:
                for times in TIME:
                    print(f"{times}) {TIME[times]}")
                enctime = int(input("Time of Day: "))
                encsum = TIME[enctime] + "/All Weather"
                print()
                print("Searching ",encsum)
                print()
                return(spawntable[encsum])
            else:
                for times in TIME:
                    print(f"{times}) {TIME[times]}")
                enctime = int(input("Time of Day: "))
                for weathers in WEATHER:
                    print(f"{weathers}) {WEATHER[weathers]}")
                encwea = int(input("Weather: "))
                encsum = TIME[enctime] + "/" + WEATHER[encwea]
                print()
                print("Searching ",encsum)
                print()
                return(spawntable[encsum])
            


if __name__ == "__main__":

    rolls = 5
    guaranteed_ivs = 0
    group_ids = [218,219,220,221,222,109,110,113,115,116]

    print("This script was created by CappyCapital using information provided by Lincoln and Santacrab420. Reach out on the /r/pokemonrng discord for more information.")
    print()
    print()

    maps = {
            1:"obsidianfieldlands",
            2:"crimsonmirelands",
            3:"cobaltcoastlands",
            4:"coronethighlands",
            5:"alabastericelands"
            }

    playermap = input("Enter your map number: \n" \
                      f"1) Obsidian Fieldlands\n" \
                      f"2) Crimson Mirelands\n" \
                      f"3) Cobalt Coastlands\n" \
                      f"4) Coronet Highlands\n" \
                      f"5) Alabaster Icelands\n")

    print()
    print("Choice: ",maps[int(playermap)])

    spawnmapurl = f"../../resources/{maps[int(playermap)]}-spawn.json"
    encmapurl = f"../../resources/{maps[int(playermap)]}.json"

    spawnmap = open(spawnmapurl)
    encmap = open(encmapurl)

    spawnmap = json.load(spawnmap)
    encmap = json.load(encmap)

    print()
    group_id = int(input(f"Enter Group ID:\n"))
    print()

    i = spawnmap[str(group_id)]['name']
    spawntable = {}
    grouplist = []

    for keys in spawnmap:
        if spawnmap[keys]['name'] == i:
            grouplist.append(str(keys))

    print("List of Group IDs that share the same spawn table:")
    print()
    print(*grouplist,sep=", ")
    print()
    
    for keys in encmap:
        if i == keys:
            spawntable = encmap[i]
            break

    spawns = get_spawns_by_category(spawntable)
    print()

    encsum = 0
    for sum in spawns:
        encsum += spawns[sum]
    
    print("Possible Pokemon At For this Time and Weather: ")
    f = 1
    for pokes in spawns:
        print(f"{f}) {pokes}")
        f+=1

    print()
    
    userpoke = int(input("Enter Species (use the number):"))
    userpoke -= 1

    userpoke = list(spawns)[userpoke]

    encmin = 0
    encmax = 0
    
    for i in spawns:
        if userpoke == i:
            encmax = encmin + spawns[i]
            break
        else:
            encmin += spawns[i]

    rolls = int(input("Shiny Rolls for Species:\n"))

    for groups in grouplist:
        print(f"checking Group {groups}: ")
        adv,group_seed,fixed_seed,ec,pid,ivs,ability,gender,nature,shiny = \
            read_wild_rng(int(groups),rolls,guaranteed_ivs,encsum,encmin,encmax)
        if group_seed == 0:
            print("Spawner is not active")
            print()
        elif adv == 40959:
            print("No seed found")
            print()
        else:
            if adv < 100:
                print(f"Closest Shiny: " + Fore.GREEN + f"{adv}" + Style.RESET_ALL)
            else:
                print(f"Closest Shiny: " + Fore.RED + f"{adv}" + Style.RESET_ALL)
            print(f"Seed: {fixed_seed:X}")
            print("Group Seed: ", hex(group_seed))
            print(f"EC: {ec:X} PID: {pid:X}")
            print(f"Nature: {Util.STRINGS.natures[nature]} Ability: {ability}")
            print(ivs)
            print()
