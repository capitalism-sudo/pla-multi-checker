# Go to root of PyNXReader
import signal
import sys
import json

from z3.z3 import TupleSort

sys.path.append('../')

from nxreader import SWSHReader
from rng import XOROSHIRO,OverworldRNG


shiny_charm = True
mark_charm = True
weather_active = True
is_fishing = False
is_static = False
min_level = 60
max_level = 65
diff_held_item = True

config = json.load(open("../config.json"))
r = SWSHReader(config["IP"])

def signal_handler(signal, frame): #CTRL+C handler
    print("Stop request")
    r.close()

signal.signal(signal.SIGINT, signal_handler)
rng = XOROSHIRO(int.from_bytes(r.read(0x4C2AAC18,8),"little"),int.from_bytes(r.read(0x4C2AAC18+8,8),"little"))
predict = OverworldRNG(rng.state(),r.TID,r.SID,shiny_charm,mark_charm,weather_active,is_fishing,is_static,min_level,max_level,diff_held_item)
advances = 0

# filter for target
def gen_filter(state):
    return True
result = predict.generate()
while not gen_filter(result):
    result = predict.generate()
print(f"Advance {advances}, State {rng.state():016X}")
print(result)
while True:
    read = int.from_bytes(r.read(0x4C2AAC18,16),"little")
    while rng.state() != read:
        rng.next()
        advances += 1
        if rng.state() == read:
            if advances >= predict.advance:
                result = predict.generate()
                while not gen_filter(result) or advances >= predict.advance:
                    result = predict.generate()
            print(f"Advance {advances}, State {rng.state():016X}")
            print(result)