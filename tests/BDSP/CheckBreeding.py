# Go to root of PyNXReader
import signal
import sys
import json
sys.path.append('../../')

from rng import Xorshift
from nxreader import BDSPReader
from structure import Daycare8b

config = json.load(open("../../config.json"))
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
print(f"S[0]: {seed[0]:08X}\tS[1]: {seed[1]:08X}\nS[2]: {seed[2]:08X}\tS[3]: {seed[3]:08X}")
print()
print(f"Advances: {advances}\n")

daycare = Daycare8b(reader.readDaycare())
egg_ready = "Yes" if daycare.present() else "No"
egg_seed = daycare.seed()
egg_steps = daycare.steps()
print(f"Is egg ready? {egg_ready}\nEgg Seed: {egg_seed:08X}\nSteps for next egg: {180 - egg_steps}\n\n")

while True:
    state = int.from_bytes(reader.readRNG(),"little")
    daycare = Daycare8b(reader.readDaycare())
    egg_ready = "Yes" if daycare.present() else "No"
    egg_seed = daycare.seed()
    egg_steps = daycare.steps()

    while rng.state != state:
        rng.next()
        advances += 1

        if rng.state == state:
            print("Current Seed")
            print(f"S[0]: {rng.seed[0]:08X}\tS[1]: {rng.seed[1]:08X}\nS[2]: {rng.seed[2]:08X}\tS[3]: {rng.seed[3]:08X}")
            print()
            print(f"Advances: {advances}\n")
            print(f"Is egg ready? {egg_ready}\nEgg Seed: {egg_seed:08X}\nSteps for next egg: {180 - egg_steps}\n\n")
