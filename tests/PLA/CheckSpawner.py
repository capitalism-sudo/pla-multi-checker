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

def read_wild_rng(spawner_id,rolls,guaranteed_ivs):
    spawner_seed = reader.read_pointer_int(f"main+4267ee0]+330]+" \
                                           f"{0x90+spawner_id*0x80:X}",8)
    wild_seed = (spawner_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF
    main_rng = XOROSHIRO(wild_seed)
    for adv in range(40960):
        rng = XOROSHIRO(*main_rng.seed.copy())
        spawner_seed = rng.next()
        rng = XOROSHIRO(spawner_seed)
        rng.next()
        fixed_seed = rng.next()
        ec,pid,ivs,ability,gender,nature,shiny = \
            generate_from_seed(fixed_seed,rolls,guaranteed_ivs)
        if shiny:
            break
        main_rng.next()
        main_rng.next()
        main_rng = XOROSHIRO(main_rng.next())
    return adv,wild_seed,fixed_seed,ec,pid,ivs,ability,gender,nature,shiny


if __name__ == "__main__":
    rolls = int(input("Shiny Rolls For Species: "))
    guaranteed_ivs = 3 if input("Alpha? (y/n): ").lower() == "y" else 0
    spawner_id = int(input("Spawner ID: "))
    
    adv,wild_seed,fixed_seed,ec,pid,ivs,ability,gender,nature,shiny = \
        read_wild_rng(spawner_id,rolls,guaranteed_ivs)
    if wild_seed == (-0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF:
        print("Spawner is not active")
    else:
        print(f"Closest Shiny: {adv}")
        print(f"Seed: {fixed_seed:X}")
        print(f"EC: {ec:X} PID: {pid:X}")
        print(f"Nature: {Util.STRINGS.natures[nature]} Ability: {ability}")
        print(ivs)
        print()