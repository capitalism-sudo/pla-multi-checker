# Go to root of PyNXReader
import signal
import sys
import json

sys.path.append('../')

from nxreader import SWSHReader
from rng import XOROSHIRO,OverworldRNG,Filter


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
em_count = 3
kos = 500

filter = Filter(
    iv_min = [31,31,31,31,31,31],
    iv_max = [31,31,31,31,31,31],
    slot_min = 0,
    slot_max = 24,
    brilliant = True
)

config = json.load(open("../config.json"))
r = SWSHReader(config["IP"])

def signal_handler(signal, frame): #CTRL+C handler
    print("Stop request")
    r.close()

signal.signal(signal.SIGINT, signal_handler)
seed = r.readRNG()
rng = XOROSHIRO(int.from_bytes(seed[0:8],"little"),int.from_bytes(seed[8:16],"little"))
predict = OverworldRNG(
    seed = rng.state,
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
    egg_move_count = em_count,
    kos = kos,
    filter = filter
    )
advances = 0

print(f"Advance {advances}, State {rng.state:016X}")
result = predict.generate()
while not result:
    result = predict.generate()
print(result)
while True:
    read = int.from_bytes(r.readRNG(),"little")
    while rng.state != read:
        rng.next()
        advances += 1
        if rng.state == read:
            if advances >= predict.advance:
                result = None
                result = predict.generate()
                while not result or advances >= predict.advance:
                    result = predict.generate()
            print(f"Advance {advances}, State {rng.state:016X}")
            print(result)