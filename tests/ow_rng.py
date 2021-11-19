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
is_static = True
min_level = 60
max_level = 60
is_legendary = False
is_shiny_locked = False
diff_held_item = False
double_mark_gen = False

# filter for target
def gen_filter(state):
    if state.xor < 16:
        return True
    return False

config = json.load(open("../config.json"))
r = SWSHReader(config["IP"])

def signal_handler(signal, frame): #CTRL+C handler
    print("Stop request")
    r.close()

signal.signal(signal.SIGINT, signal_handler)
rng = XOROSHIRO(int.from_bytes(r.read(0x4C2AAC18,8),"little"),int.from_bytes(r.read(0x4C2AAC18+8,8),"little"))
predict = OverworldRNG(
    seed = rng.state(),
    tid = r.TID,
    sid = r.SID,
    shiny_charm = shiny_charm,
    mark_charm = mark_charm,
    weather_active = weather_active,
    is_fishing = is_fishing,
    is_legendary = is_legendary,
    is_shiny_locked = is_shiny_locked,
    is_static = is_static,
    min_level = min_level,
    max_level = max_level,
    diff_held_item = diff_held_item,
    double_mark_gen = double_mark_gen,
    )
advances = 0

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