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
rng = Xorshift(state >> 96, (state >> 64) & 0xFFFFFFFF, (state >> 32) & 0xFFFFFFFF, state & 0xFFFFFFFF)
seed = rng.seed
advances = 0
print("Initial Seed")
print(f"S[0]: {seed[0]:08X}\tS[1]: {seed[1]:08X}\nS[2]: {seed[2]:08X}\tS[3]: {seed[3]:08X}")
print()
print(f"Advances: {advances}\n")

while True:
    state = reader.readRNG()
    while rng.state != state:
        rng.next()
        advances += 1
        if rng.state == state:
            print("Current Seed")
            print(f"S[0]: {rng.seed[0]:08X}\tS[1]: {rng.seed[1]:08X}\nS[2]: {rng.seed[2]:08X}\tS[3]: {rng.seed[3]:08X}")
            print()
            print(f"Advances: {advances}\n")