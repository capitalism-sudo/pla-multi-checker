# Go to root of PyNXReader
import signal
import sys
import json

sys.path.append('../')

from nxreader import SWSHReader
from rng import XOROSHIRO,OverworldRNG


config = json.load(open("../config.json"))
r = SWSHReader(config["IP"])

def signal_handler(signal, frame): #CTRL+C handler
    print("Stop request")
    r.close()

signal.signal(signal.SIGINT, signal_handler)
rng = XOROSHIRO(int.from_bytes(r.read(0x4C2AAC18,8),"little"),int.from_bytes(r.read(0x4C2AAC18+8,8),"little"))
predict = OverworldRNG(seed=rng.state(),tid=r.TID,sid=r.SID,shiny_charm=True,mark_charm=True,weather_active=True,is_fishing=False,is_static=True,min_level=60,max_level=60,diff_held_item=False)
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