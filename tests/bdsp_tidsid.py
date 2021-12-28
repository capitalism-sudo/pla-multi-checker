# Go to root of PyNXReader
import signal
import sys
import json
sys.path.append('../')

from rng import Xorshift,BDSPIDGenerator
from nxreader import BDSPReader

config = json.load(open("../config.json"))
reader = BDSPReader(config["IP"],usb_connection=config["USB"])

def signal_handler(signal, advances): #CTRL+C handler
    print("Stop request")
    reader.close()

signal.signal(signal.SIGINT, signal_handler)

# list of g8tids to filter for
filter = [
123456,
654321,
777000,
]


state = reader.readRNG()
rng = Xorshift(int.from_bytes(state[0:4],"little"), int.from_bytes(state[4:8],"little"), int.from_bytes(state[8:12],"little"), int.from_bytes(state[12:16],"little"))
seed = rng.seed
print("Initial Seed")
print(f"S[0]: {seed[0]:08X}\tS[1]: {seed[1]:08X}\nS[2]: {seed[2]:08X}\tS[3]: {seed[3]:08X}")
gen = BDSPIDGenerator(seed)
for adv in range(500):
    sidtid,tid,sid,g8tid,tsv = gen.generate()
    if g8tid in filter:
        print(f"{adv} {g8tid:06d} {sidtid:08X} {tid:05d}/{sid:05d} {tsv:04d}")