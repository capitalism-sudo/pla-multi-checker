# Go to root of PyNXReader
import signal
import sys
import json
from time import sleep
sys.path.append('../../')

from nxreader import NXReader
from structure import PK9
from rng import XOROSHIRO
from lookups import Util


config = json.load(open("../../config.json"))
reader = NXReader(config["IP"],usb_connection=config["USB"])

def signal_handler(signal, advances): #CTRL+C handler
    print("Stop request")
    reader.close()

signal.signal(signal.SIGINT, signal_handler)

def battle(index):
    return PK9(reader.read_pointer(f"main+4267f00]+b0]+e0]+d0]+{0xb0+8*(index+6):X}]+70]+60]+98]+10]",PK9.STOREDSIZE))

def generate_from_seed(seed,rolls,guaranteed_ivs=0):
    rng = XOROSHIRO(seed)
    ec = rng.rand(0xFFFFFFFF)
    sidtid = rng.rand(0xFFFFFFFF)
    for _ in range(rolls):
        pid = rng.rand(0xFFFFFFFF)
        shiny = ((pid >> 16) ^ (sidtid >> 16) ^ (pid & 0xFFFF) ^ (sidtid & 0xFFFF)) < 0x10
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
    ability = rng.rand(2) # rand(3) if ha possible?
    gender = rng.rand(252) + 1 # if set gender then dont roll
    nature = rng.rand(25)
    return ec,pid,ivs,ability,gender,nature,shiny

def read_wild_seed(i):
    spawner_seed = reader.read_pointer_int(f"main+4267ee0]+330]+{0x70+i*0x80+0x20:X}",8)
    return (spawner_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF

def check_spawner_id(rolls,guaranteed_ivs):
    while True:
        mon = battle(0)
        print("Battle:")
        print(mon)
        seeds = XOROSHIRO.find_seeds_arceus(mon.ec,mon.pid,rolls)
        print("Possible fixed seeds:")
        print(seeds)
        seed = None
        for test in seeds:
            ec,pid,ivs,ability,gender,nature,shiny = generate_from_seed(test,rolls,guaranteed_ivs)
            if ivs == mon.ivs:
                seed = test
                print(f"Found fixed seed: {seed:X}")
                break
        if seed is None:
            print(f"Could not calculate fixed seed")
            exit()
        read = None
        i = 0
        while read != seed and i < 3500:
            s = reader.read_pointer_int(f"main+4267ee0]+330]+{0x70+i*0x80+0x20:X}",8)
            if s != 0:
                rng = XOROSHIRO(s)
                rng.next()
                read = rng.next()
                print(f"{read:X} {i/35}%")
            i += 1
        if i != 3500:
            print(f"Found at id {i-1}")
            exit()

if __name__ == "__main__":
    rolls = int(input("Shiny Rolls For Species: "))
    guaranteed_ivs = 3 if input("Alpha? (y/n): ").lower() == "y" else 0
    check_spawner_id(rolls,guaranteed_ivs)