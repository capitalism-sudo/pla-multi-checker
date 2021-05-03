# Script to read overworld pokemon
# Save the game to update the KCoordinates block

# Go to root of PyNXReader
import sys
import json
import signal
sys.path.append('../')

from nxreader import SWSHReader
from structure import KCoordinates

# Connect to Switch
config = json.load(open("../config.json"))
r = SWSHReader(config["IP"])

def signal_handler(signal, frame): #CTRL+C handler
    print("Stop request")
    r.close()

signal.signal(signal.SIGINT, signal_handler)

# Give the KCoords class access to the switch
r.KCoordinates.r = r
last_info = []
while True:
    # Refresh KCoords block
    r.KCoordinates = KCoordinates(r.readKCoordinatesBlock())
    pkms = r.KCoordinates.ReadOwPokemonFromBlock()
    info = []
    for pkm in pkms:
        info.append(pkm.toString())
    if info != last_info:
        last_info = info
        for pkm in info:
            print(pkm)
        print("-------------------------------")
    r.pause(0.3)
r.close()
