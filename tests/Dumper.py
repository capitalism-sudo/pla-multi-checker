# Go to root of PyNXReader
import sys
sys.path.append('../')
from nxreader import SWSHReader
import json

DumpPath = 'Event/PersonalDump/'
config = json.load(open("../config.json"))

r = SWSHReader(config["IP"],usb_connection=config["USB"])

print("Dumping bonus_rewards...")
r.readEventBlock_BonusRewards(DumpPath)
print("Dumping dai_encount...")
r.readEventBlock_CrystalEncounter(DumpPath)
print("Dumping drop_rewards...")
r.readEventBlock_DropRewards(DumpPath)
print("Dumping normal_encount...")
r.readEventBlock_RaidEncounter(DumpPath)
print("Dumping normal_encount_rigel1...")
r.readEventBlock_RaidEncounter_IoA(DumpPath)
print("Dumping normal_encount_rigel2...")
r.readEventBlock_RaidEncounter_CT(DumpPath)

print("\nDump completed!\n")

r.close()
