# Desired IVs
V6 = [31,31,31,31,31,31]
S0 = [31,31,31,31,31,00]
A0 = [31,00,31,31,31,31]

# Desired Nature
Nature = "Careful"

useFilters = True
MaxResults = 1000
doResearch = True

# Go to root of PyNXReader
import signal
import sys
import json
sys.path.append('../')

from lookups import Util
from nxreader import RaidReader
from rng import XOROSHIRO,Raid
from structure import Den

def signal_handler(signal, frame): #CTRL+C handler
    print("Stop request")
    b.close()

config = json.load(open("../config.json"))
r = RaidReader(config["IP"])

signal.signal(signal.SIGINT, signal_handler)

seed = None

for ii in range(RaidReader.DENCOUNT):
    if ii > 189:
        den = Den(r.readDen(ii + 32))
    elif ii > 99:
        den = Den(r.readDen(ii + 11))
    else:
        den = Den(r.readDen(ii))
    if den.isActive():
        spawn = den.getSpawn(denID = ii, isSword = r.isPlayingSword)
        currShinyLock = 0
        if ii > 189:
            info = f"[CT] denID: {ii-189}"
        elif ii > 99:
            info = f"[IoA] denID: {ii-99}"
        else:
            info = f"denID: {ii+1}"
        info += f"    {den.stars()}★    Species: {Util.STRINGS.species[spawn.Species()]}"
        if spawn.IsGigantamax():
            info += " G-Max"
        if den.isEvent():
            info += "    Event"
            currShinyLock = spawn.ShinyFlag()
        if den.isWishingPiece():
            if currShinyLock != 2:
                info += f"    Next Shiny Frame: {Raid.getNextShinyFrame(den.seed())}"
            else:
                info += f"    Next Shiny Frame: 0"
            seed = den.seed()
            info = "!!! " + info
            piecedSpawn = spawn
            piecedShinyLock = currShinyLock
        print(info)
        raid = Raid(seed = den.seed(), TID = r.TID, SID = r.SID, flawlessiv = spawn.FlawlessIVs(), shinyLock = currShinyLock, ability = spawn.Ability(), gender = spawn.Gender(), species = spawn.Species(), altform = spawn.AltForm())
        raid.print()
        print()

# Choose RNGable den to calculate frames
if seed is not None and doResearch:
    print('\nWishing Piece Den Prediction:\n')
    i = 0
    while i < MaxResults:
        raid = Raid(seed, TID = b.TID, SID = b.SID, flawlessiv = piecedSpawn.FlawlessIVs(), shinyLock = piecedShinyLock, ability = piecedSpawn.Ability(), gender = piecedSpawn.Gender(), species = piecedSpawn.Species(), altform = piecedSpawn.AltForm())
        seed = XOROSHIRO(seed).next()
        if useFilters:
            if (raid.ShinyType != 'None' or raid.IVs == V6 or raid.IVs == S0 or raid.IVs == A0) and Util.STRINGS.natures[raid.Nature] == Nature:
                print(f"Frame:{i}")
                raid.print()
                print()
        else:
            print(f"Frame:{i}")
            raid.print()
            print()
        i += 1

b.close()
