# Go to root of PyNXReader
import sys
import json
sys.path.append('../')

from nxreader import SWSHReader

config = json.load(open("../config.json"))
r = SWSHReader(config["IP"],usb_connection=config["USB"])

print(f"TID: {r.TrainerSave.TID()}")
print(f"SID: {r.TrainerSave.SID()}")
print(f"TSV: {r.TrainerSave.TSV()}")
print(f"Language: {r.TrainerSave.getLangName()}")
print(f"Money: {r.TrainerSave.Money()}$")
print(f"Watts: {r.TrainerSave.Watts()}\n")

r.close()
