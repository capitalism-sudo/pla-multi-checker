# Go to root of PyNXReader
import signal
import sys
import json
sys.path.append('../')

from rng import Xorshift
from nxreader import BDSPReader

config = json.load(open("../config.json"))
reader = BDSPReader(config["IP"],usb_connection=config["USB"])

def signal_handler(signal, advances): #CTRL+C handler
    print("Stop request")
    reader.close()

signal.signal(signal.SIGINT, signal_handler)

state = reader.readRNG()
rng = Xorshift(int.from_bytes(state[0:4],"little"), int.from_bytes(state[4:8],"little"), int.from_bytes(state[8:12],"little"), int.from_bytes(state[12:16],"little"))
seed = rng.seed
advances = 0
print("Initial Seed")
print(f"S[01]: {rng.seed[0]:08X}{rng.seed[1]:08X}\tS[23]: {rng.seed[2]:08X}{rng.seed[3]:08X}")
print(f"S[0]: {seed[0]:08X}\tS[1]: {seed[1]:08X}\nS[2]: {seed[2]:08X}\tS[3]: {seed[3]:08X}")
print()
print(f"Advances: {advances}\n")

target = input("Target Frame? (enter for None): ")
mod = None

if target != '':
    target = int(target)
    mod = int(input("Modulo: "))
else: 
    target = None

while True:
    state = int.from_bytes(reader.readRNG(),"little")
    change = 0
    while rng.state != state:
        rng.next()
        change += 1
        if rng.state == state:
            advances += change
            print("Current Seed")
            print(f"S[01]: {rng.seed[0]:08X}{rng.seed[1]:08X}\tS[23]: {rng.seed[2]:08X}{rng.seed[3]:08X}")
            print(f"S[0]: {rng.seed[0]:08X}\tS[1]: {rng.seed[1]:08X}\nS[2]: {rng.seed[2]:08X}\tS[3]: {rng.seed[3]:08X}")
            print()
            print(f"Advances: {advances}")
            print(f"\t+ {change}\n")
            if target is not None:
                print(f"{target-advances} to target, {(target-advances)%mod} away from a multiple of mod") 
    reader.pause(0.3)