# Go to root of PyNXReader
import sys
import json
sys.path.append('../')

from structure import PK8
from nxreader import SWSHReader

config = json.load(open("../config.json"))
r = SWSHReader(config["IP"],usb_connection=config["USB"])

for ii in range(1,7):
    print(f"Slot: {ii}")
    pk8 = PK8(r.readParty(ii))
    if pk8.isValid and pk8.ec != 0:
        print(pk8)
    else:
        print('Empty')

print()
r.close()
