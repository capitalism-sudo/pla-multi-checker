# Go to root of PyNXReader
import sys
import json
sys.path.append('../')

from structure import PK8
from nxreader import SWSHReader

config = json.load(open("../config.json"))
r = SWSHReader(config["IP"],usb_connection=config["USB"])

while True:
    pk8 = PK8(r.readHorse())
    if pk8.isValid and pk8.ec != 0:
        print(pk8)
    else:
        print("No horse fused\n")
    stop = input("Check again? (y/n): ")
    print()
    if stop == 'n' or stop == 'N':
        r.close()
