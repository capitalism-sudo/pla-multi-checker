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

def read_mass_outbreak_rng(group_id,rolls):
    generator_seed = reader.read_pointer_int(f"main+4268ee0]+330]+{0x70+group_id*0x440+0x20:X}",8)
    group_seed = (generator_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF
    main_rng = XOROSHIRO(group_seed)
    for advance in range(100):
        for init_spawn in range(4):
            generator_seed = main_rng.next()
            main_rng.next() # spawner 1's seed, unused
            fixed_rng = XOROSHIRO(generator_seed)
            fixed_rng.next()
            fixed_seed = fixed_rng.next()
            ec,pid,ivs,ability,gender,nature,shiny = generate_from_seed(fixed_seed,rolls)
            if shiny:
                print(f"{generator_seed:X} Advance {advance} Init Spawn {init_spawn} EC: {ec:08X} PID: {pid:08X} {'/'.join(str(iv) for iv in ivs)}")
        group_seed = main_rng.next()
        main_rng = XOROSHIRO(group_seed)
        respawn_rng = XOROSHIRO(group_seed)
        for respawn in range(1,9):
            generator_seed = respawn_rng.next()
            respawn_rng.next() # spawner 1's seed, unused
            respawn_rng = XOROSHIRO(respawn_rng.next())
            fixed_rng = XOROSHIRO(generator_seed)
            fixed_rng.next()
            fixed_seed = fixed_rng.next()
            ec,pid,ivs,ability,gender,nature,shiny = generate_from_seed(fixed_seed,rolls)
            if shiny:
                print(f"{generator_seed:X} Advance {advance} Respawn {respawn} EC: {ec:08X} PID: {pid:08X} {'/'.join(str(iv) for iv in ivs)}")


if __name__ == "__main__":
    rolls = int(input("Shiny Rolls For Species: "))
    group_id = int(input("Group ID: "))
    
    read_mass_outbreak_rng(group_id,rolls)