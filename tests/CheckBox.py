# Go to root of PyNXReader
import sys
import json
sys.path.append('../')

from structure import PK8
from nxreader import SWSHReader

config = json.load(open("../config.json"))
r = SWSHReader(config["IP"],usb_connection=config["USB"])

while True:
    empty = True
    box = int(input('Which box would you like to check? '))
    print()
    for ii in range(1,31):
        pk8 = PK8(r.readBox(box,ii))
        if pk8.isValid and pk8.ec != 0:
            print(f"Box: {box} Slot: {ii}")
            print(pk8)
            empty = False
    if empty:
        print('Box is empty\n')
    stop = input('Continue? (y/n) ' )
    if stop != 'y' and stop != 'Y':
        break

r.close()
