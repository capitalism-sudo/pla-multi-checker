# Go to root of PyNXReader
import signal
import sys
import json

sys.path.append('../')

# no BDSPReader yet
from nxreader import NXReader
from rng import XorShift,BDSPStationaryGenerator

rng_pointer = "[main+4F8CCD0]"

config = json.load(open("../config.json"))
r = NXReader(config["IP"])

def signal_handler(signal, frame): #CTRL+C handler
    print("Stop request")
    r.close()

signal.signal(signal.SIGINT, signal_handler)

initial = r.read_pointer(rng_pointer, 16)
track = XorShift(int.from_bytes(initial[:8], "little"), int.from_bytes(initial[8:], "little"))
predict = BDSPStationaryGenerator(*track.seed())
shiny = False
while not shiny:
    target, shiny = predict.generate()
advances = 0

while True:
    state = int.from_bytes(r.read_pointer(rng_pointer, 16), "little")

    while state != track.state():
        track.next()
        advances += 1

        if state == track.state():
            if advances > target:
                shiny = False
                while not shiny:
                    target, shiny = predict.generate()
            go = XorShift(*track.seed())
            curr_id = go.next()
            curr_shiny = go.next()

            print(f"Advance: {advances}")
            print(go)
            print(f"ID: {curr_id:08X} - Shiny: {curr_shiny:08X}")
            print(f"Target: {target}")
            print(f"In: {target-advances}")
            print()
    r.pause(0.1)