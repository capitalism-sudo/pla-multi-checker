# Go to root of PyNXReader
import signal
import sys
import json
sys.path.append('../../')

from nxreader import NXReader
from rng import XOROSHIRO
from lookups import Util


config = json.load(open("../../config.json"))
reader = NXReader(config["IP"],usb_connection=config["USB"])

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

def read_wild_rng(group_id,rolls,guaranteed_ivs,encounter_slot_sum,encounter_slot_range):
    group_seed = reader.read_pointer_int(f"main+4268ee0]+330]+{0x70+group_id*0x440+0x408:X}",8)
    main_rng = XOROSHIRO(group_seed)
    adv = -1
    while True:
        adv += 1
        rng = XOROSHIRO(*main_rng.seed.copy())
        spawner_seed = rng.next()
        rng = XOROSHIRO(spawner_seed)
        encounter_slot = (rng.next()/(2**64))*encounter_slot_sum
        fixed_seed = rng.next()
        ec,pid,ivs,ability,gender,nature,shiny = \
            generate_from_seed(fixed_seed,rolls,guaranteed_ivs)
        if shiny and encounter_slot_range[0] <= encounter_slot <= encounter_slot_range[1]:
            break
        main_rng.next()
        main_rng.next()
        main_rng = XOROSHIRO(main_rng.next())
    return adv,group_seed,fixed_seed,ec,pid,ivs,ability,gender,nature,shiny


if __name__ == "__main__":
    print("Whipping up a distortion! Don't do it too fast!")
    cont = True
    while cont:
        reader.write_main_int(0x24672A4,0x5280010A,4)
        reader.write_main_int(0x24672A4,0x7100052A,4)
        cont = True if input("Want Another? y/n").lower() == 'y' else False

    
