# Go to root of PyNXReader
import signal
import sys
import json
import colorama
sys.path.append('../../')

from nxreader import NXReader
from rng import XOROSHIRO
from lookups import Util
from colorama import Fore, Back, Style

obsidiangr = {
    (0,4): "Horseshoe Plains",
    (4,8): "Windswept Run",
    (8,12): "Nature's Pantry",
    (12,16): "Sandgem Flats"}

miregr = {
    (0,4): "Droning Meadow",
    (4,8): "Holm of Trials",
    (8,12): "Unknown",
    (12,16): "Ursa's Landing",
    (16,20): "Prairie",
    (20,24): "Gapejaw Bog"}

cobaltgr = {
    (0,4): "Ginko Landing",
    (4,8): "Aipom Hill",
    (8,12): "Deadwood Haunt",
    (12,16): "Spring Path",
    (16,20): "Windbreak Stand"}

coronetgr = {
    (0,4): "Sonorous Path",
    (4,8): "Ancient Quarry",
    (8,12): "Celestica Ruins",
    (12,16): "Primeval Grotto",
    (16,20): "Boulderoll Ravine"}

icelandsgr = {
    (0,4): "Bonechill Wastes North",
    (4,8): "Avalugg's Legacy",
    (8,12): "Bonechill Wastes South",
    (12,16): "Southeast of Arena",
    (16,20): "Heart's Crag",
    (20,24): "Arena's Approach"}


config = json.load(open("../../config.json"))
reader = NXReader(config["IP"],usb_connection=config["USB"])
colorama.init()

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
    ability = rng.rand(2)+1 # rand(3) if ha possible
    if set_gender:
        gender = -1
    else:
        gender = rng.rand(252) + 1
    nature = rng.rand(25)
    return ec,pid,ivs,ability,gender,nature,shiny

def read_wild_rng(group_id,rolls,guaranteed_ivs,encounter_slot_sum,encounter_slot_range,mapval):
    group_seed = group_id
    main_rng = XOROSHIRO(group_seed)
    set_gender = False
    adv = -1
    while True:
        adv += 1
        rng = XOROSHIRO(*main_rng.seed.copy())
        spawner_seed = rng.next()
        rng = XOROSHIRO(spawner_seed)
        encounter_slot = (rng.next()/(2**64))*encounter_slot_sum
#       """Mire Porygon Set Gender"""
        if mapval == 2:
            if encounter_slot < 118:
                set_gender = True
            else:
                set_gender = False
         #       """coastlands set gender"""
        elif mapval == 3:
            set_gender = True
        fixed_seed = rng.next()
        ec,pid,ivs,ability,gender,nature,shiny = \
            generate_from_seed(fixed_seed,rolls,guaranteed_ivs,set_gender)
        break
        main_rng.next()
        main_rng.next()
        main_rng = XOROSHIRO(main_rng.next())
    return adv,group_seed,fixed_seed,ec,pid,ivs,ability,gender,nature,shiny,encounter_slot


if __name__ == "__main__":

    """This toggle sets the map. Here are the values:
    1 - Obsidian Firelands
    2 - Crimson Mirelands
    3 - Cobalt Coastlands
    4 - Coronet Highlands
    5 - Alabaster Icelands

    Set map to the location you're hunting in.
    """
    mapval = 2
    
    rolls = int(input(f"Shiny Rolls: \n"))
    guaranteed_ivs = 0
    shinyfilter = True if input("Shinyfilter? y/n: ").lower() == "y" else False
    dist = 13

    locgr = obsidiangr

    if mapval == 2:
        locgr = miregr
    elif mapval == 3:
        locgr = cobaltgr
    elif mapval ==4:
        locgr = coronetgr
    elif mapval ==5:
        locgr = icelandsgr

    if mapval == 2:
        dist = 24
    elif mapval == 3 or mapval == 4:
        dist = 20
    elif mapval == 5:
        dist = 24


    for i in range(0,dist):
        print(f"Checking Group {i}:")
        for location in locgr:
            if i in location:
                locvar = locgr[location]
#Obsidian Fieldlands
        if mapval == 1:
            generator_seed = reader.read_pointer_int(f"[[[[[[main+428E268]+C0]+1C0]+{0x980 + i*0x8:X}]+18]+428]+C8",8)
#Crimson Mirelands
        elif mapval == 2:
            generator_seed = reader.read_pointer_int(f"[[[[[[main+428E268]+C0]+1C0]+{0xC78 + i*0x8:X}]+18]+428]+C8",8)
#Cobalt Coastlands
        elif mapval == 3:
            generator_seed = reader.read_pointer_int(f"[[[[[[main+428E268]+C0]+1C0]+{0xCC0 + i*0x8:X}]+18]+428]+C8",8)
#Coronet Highlands
        elif mapval == 4:
            generator_seed = reader.read_pointer_int(f"[[[[[[main+428E268]+C0]+1C0]+{0x828 + i*0x8:X}]+18]+428]+C8",8)
#            generator_seed = reader.read_pointer_int(f"[[[[[[main+428E268]+C0]+1C0]+{0x828 + i*0x8:X}]+18]+428]+D8",8)
#Alabaster Icelands
        elif mapval == 5:
            generator_seed = reader.read_pointer_int(f"[[[[[[main+428E268]+C0]+1C0]+{0x948 + i*0x8:X}]+18]+428]+C8",8)
        encounter_slot_sum = 112
        encounter_slot_range = (0,112)
        if mapval == 2:
            encounter_slot_sum = 276
            encounter_slot_range = (0,276)
        elif mapval == 3:
            encounter_slot_sum = 163
            encounter_slot_range = (0,163)
        elif mapval == 4:
            encounter_slot_sum = 382
            encounter_slot_range = (0,382)
        elif mapval == 5:
            encounter_slot_sum = 259
            encounter_slot_range = (0,259)
        if i >=13 and i <=15 and mapval==2:
            encounter_slot_sum = 118
            encounter_slot_range = (0,118)
        group_id = (generator_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF
        print()
        adv,group_seed,fixed_seed,ec,pid,ivs,ability,gender,nature,shiny,encslot = \
            read_wild_rng(group_id,rolls,guaranteed_ivs,encounter_slot_sum,encounter_slot_range,mapval)
        if group_seed == 0:
            print("Spawner is not active")
        else:
            if shiny and shinyfilter:
                if i not in [0,4,8,12,16,20] and locvar.lower() != "unknown":
                    print(f"Generator Seed: {hex(generator_seed)}")
                    if shiny:
                        print(f"Shiny: " + Back.GREEN + f"{shiny}" + Style.RESET_ALL)
                    else:
                        print(f"Shiny: " + Fore.RED + f"{shiny}" + Style.RESET_ALL)
                    print(f"Location: {locvar}")
                    if mapval==1:
                        print(f"Encounter Slot: {encslot}")
                        if encslot < 100:
                            print(f"Species: Sneasel")
                        elif encslot >100 and encslot < 101:
                            print(f"Species: AlphaSneasel")
                        elif encslot > 101 and encslot < 111:
                            print(f"Species: Weavile")
                        elif encslot > 111 and encslot < 112:
                            print(f"Species: AlphaWeavile")
                    elif mapval==2:
                        print(f"Encounter Slot: {encslot}")
                        if encslot < 100:
                            print(f"Species: Porygon")
                        elif encslot >100 and encslot < 101:
                            print(f"Species: AlphaPorygon")
                        elif encslot > 101 and encslot < 111:
                            print(f"Species: Porygon2")
                        elif encslot > 111 and encslot < 112:
                            print(f"Species: AlphaPorygon2")
                        elif encslot > 112 and encslot < 117:
                            print(f"Species: Porygon-Z")
                        elif encslot > 117 and encslot < 118:
                            print(f"Species: AlphaPorygon-Z")
                        elif encslot > 118 and encslot < 218:
                            print(f"Species: Cyndaquil")
                        elif encslot > 218 and encslot < 219:
                            print(f"Species: AlphaCyndaquil")
                        elif encslot > 219 and encslot < 269:
                            print(f"Species: Quilava")
                        elif encslot >269 and encslot <270:
                            print(f"Species: AlphaQuilava")
                        elif encslot >270 and encslot <275:
                            print(f"Species: Typhlosion")
                        else:
                            print(f"Species: AlphaTyphlosion")
                    elif mapval==3:
                        print(f"Encounter Slot: {encslot}")
                        if encslot < 100:
                            print(f"Species: Magnemite")
                        elif encslot >100 and encslot <101:
                            print(f"Species: AlphaMagnemite")
                        elif encslot >101 and encslot <151:
                            print(f"Species: Magneton")
                        elif encslot >151 and encslot <152:
                            print(f"Species: AlphaMagneton")
                        elif encslot >152 and encslot <162:
                            print(f"Species: Magnezone")
                        else:
                            print(f"Species: AlphaMagnezone")
                    elif mapval==4:
                        print(f"Encounter Slot: {encslot}")
                        if encslot < 100:
                            print(f"Species: Cranidos")
                        elif encslot >100 and encslot < 101:
                            print(f"Species: AlphaCranidos")
                        elif encslot > 101 and encslot < 111:
                            print(f"Species: Rampardos")
                        elif encslot > 111 and encslot < 112:
                            print(f"Species: AlphaRampardos")
                        elif encslot > 112 and encslot < 212:
                            print(f"Species: Shieldon")
                        elif encslot > 212 and encslot < 213:
                            print(f"Species: AlphaShieldon")
                        elif encslot > 213 and encslot < 223:
                            print(f"Species: Bastiodon")
                        elif encslot > 223 and encslot < 224:
                            print(f"Species: AlphaBastiodon")
                        elif encslot > 224 and encslot < 324:
                            print(f"Species: Rowlet")
                        elif encslot >324 and encslot <325:
                            print(f"Species: AlphaRowlet")
                        elif encslot >325 and encslot <375:
                            print(f"Species: Dartrix")
                        elif encslot >375 and encslot <376:
                            print(f"Species: AlphaDartrix")
                        elif encslot >376 and encslot <381:
                            print(f"Species: Decidueye")
                        else:
                            print(f"Species: AlphaDecidueye")
                    elif mapval==5:
                        print(f"Encounter Slot: {encslot}")
                        if encslot < 100:
                            print(f"Species: Scizor")
                        elif encslot >100 and encslot < 101:
                            print(f"Species: AlphaScizor")
                        elif encslot > 101 and encslot < 201:
                            print(f"Species: Oshawott")
                        elif encslot > 201 and encslot < 202:
                            print(f"Species: AlphaOshawott")
                        elif encslot > 202 and encslot < 252:
                            print(f"Species: Dewott")
                        elif encslot > 252 and encslot < 253:
                            print(f"Species: AlphaDewott")
                        elif encslot > 253 and encslot < 258:
                            print(f"Species: Samurott")
                        else:
                            print(f"Species: AlphaSamurott")
                    print(f"EC: {ec:X} PID: {pid:X}")
                    print(f"Nature: {Util.STRINGS.natures[nature]} Ability: {ability}")
                    print(ivs)
                    print()
                else:
                    print("This is a common spawn, ignoring.")
                    print()
            elif not shinyfilter:
                if i not in [0,4,8,12,16,20] and locvar.lower() != "unknown":
                    print(f"Shinyfilter: {shinyfilter}")
                    print(f"Generator Seed: {hex(generator_seed)}")
                    if shiny:
                        print(f"Shiny: " + Back.GREEN + f"{shiny}" + Style.RESET_ALL)
                    else:
                        print(f"Shiny: " + Fore.RED + f"{shiny}" + Style.RESET_ALL)
                    print(f"Location: {locvar}")
                    print(f"Encounter Slot: {encslot}")
                    if mapval==1:
                        print(f"Encounter Slot: {encslot}")
                        if encslot < 100:
                            print(f"Species: Sneasel")
                        elif encslot >100 and encslot < 101:
                            print(f"Species: AlphaSneasel")
                        elif encslot > 101 and encslot < 111:
                            print(f"Species: Weavile")
                        elif encslot > 111 and encslot < 112:
                            print(f"Species: AlphaWeavile")
                    elif mapval == 2:
                        if encslot < 100:
                            print(f"Species: Porygon")
                        elif encslot >100 and encslot < 101:
                            print(f"Species: AlphaPorygon")
                        elif encslot > 101 and encslot < 111:
                            print(f"Species: Porygon2")
                        elif encslot > 111 and encslot < 112:
                            print(f"Species: AlphaPorygon2")
                        elif encslot > 112 and encslot < 117:
                            print(f"Species: Porygon-Z")
                        elif encslot > 117 and encslot < 118:
                            print(f"Species: AlphaPorygon-Z")
                        elif encslot > 118 and encslot < 218:
                            print(f"Species: Cyndaquil")
                        elif encslot > 218 and encslot < 219:
                            print(f"Species: AlphaCyndaquil")
                        elif encslot > 219 and encslot < 269:
                            print(f"Species: Quilava")
                        elif encslot >269 and encslot <270:
                            print(f"Species: AlphaQuilava")
                        elif encslot >270 and encslot <275:
                            print(f"Species: Typhlosion")
                        else:
                            print(f"Species: AlphaTyphlosion")
                    elif mapval==3:
                        print(f"Encounter Slot: {encslot}")
                        if encslot < 100:
                            print(f"Species: Magnemite")
                        elif encslot >100 and encslot <101:
                            print(f"Species: AlphaMagnemite")
                        elif encslot >101 and encslot <151:
                            print(f"Species: Magneton")
                        elif encslot >151 and encslot <152:
                            print(f"Species: AlphaMagneton")
                        elif encslot >152 and encslot <162:
                            print(f"Species: Magnezone")
                        else:
                            print(f"Species: AlphaMagnezone")
                    elif mapval==4:
                        if encslot < 100:
                            print(f"Species: Cranidos")
                        elif encslot >100 and encslot < 101:
                            print(f"Species: AlphaCranidos")
                        elif encslot > 101 and encslot < 111:
                            print(f"Species: Rampardos")
                        elif encslot > 111 and encslot < 112:
                            print(f"Species: AlphaRampardos")
                        elif encslot > 112 and encslot < 212:
                            print(f"Species: Shieldon")
                        elif encslot > 212 and encslot < 213:
                            print(f"Species: AlphaShieldon")
                        elif encslot > 213 and encslot < 223:
                            print(f"Species: Bastiodon")
                        elif encslot > 223 and encslot < 224:
                            print(f"Species: AlphaBastiodon")
                        elif encslot > 224 and encslot < 324:
                            print(f"Species: Rowlet")
                        elif encslot >324 and encslot <325:
                            print(f"Species: AlphaRowlet")
                        elif encslot >325 and encslot <375:
                            print(f"Species: Dartrix")
                        elif encslot >375 and encslot <376:
                            print(f"Species: AlphaDartrix")
                        elif encslot >376 and encslot <381:
                            print(f"Species: Decidueye")
                        else:
                            print(f"Species: AlphaDecidueye")
                    if mapval==5:
                        if encslot < 100:
                            print(f"Species: Scizor")
                        elif encslot >100 and encslot < 101:
                            print(f"Species: AlphaScizor")
                        elif encslot > 101 and encslot < 201:
                            print(f"Species: Oshawott")
                        elif encslot > 201 and encslot < 202:
                            print(f"Species: AlphaOshawott")
                        elif encslot > 202 and encslot < 252:
                            print(f"Species: Dewott")
                        elif encslot > 252 and encslot < 253:
                            print(f"Species: AlphaDewott")
                        elif encslot > 253 and encslot < 258:
                            print(f"Species: Samurott")
                        else:
                            print(f"Species: AlphaSamurott")
                    print(f"EC: {ec:X} PID: {pid:X}")
                    print(f"Nature: {Util.STRINGS.natures[nature]} Ability: {ability}")
                    print(ivs)
                    print()
                else:
                    print("This is a common spawn, ignoring.")
                    print()
            else:
                print(f"Sorry, no shiny found for Group {i}, try again!\n")
