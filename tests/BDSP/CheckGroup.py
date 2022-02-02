# Go to root of PyNXReader
import signal
import sys
import json
sys.path.append('../../')

from rng import LCRNG
from nxreader import BDSPReader

class ARNG64(LCRNG):
    mult = 0x6C078965
    add = 1
    size = 64

config = json.load(open("../../config.json"))
reader = BDSPReader(config["IP"],usb_connection=config["USB"])

def signal_handler(signal, advances): #CTRL+C handler
    print("Stop request")
    reader.close()

signal.signal(signal.SIGINT, signal_handler)

state = reader.readGroupSeed(1)
rng = ARNG64(int.from_bytes(state,"little"))
seed = rng.seed
advances = 0
print("Initial Seed")
print(f"S: {rng.seed:016X}")
print()
print(f"Advances: {advances}\n")

while True:
    state = int.from_bytes(reader.readGroupSeed(1),"little")
    change = 0
    while rng.seed != state:
        rng.next()
        change += 1
        print(hex(rng.seed), hex(state))
        if rng.seed == state:
            advances += change
            print("Current Seed")
            print(f"S: {rng.seed:016X}")
            print()
            print(f"Advances: {advances}")
            print(f"\t+ {change}")