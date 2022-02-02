# Go to root of PyNXReader
import signal
import sys
import json
sys.path.append('../../')

from nxreader import BDSPReader
from structure import PK8


config = json.load(open("../../config.json"))
reader = BDSPReader(config["IP"],usb_connection=config["USB"])

def signal_handler(signal, advances): #CTRL+C handler
    print("Stop request")
    reader.close()

signal.signal(signal.SIGINT, signal_handler)
for i in range(6):
    pk8 = PK8(reader.readParty(i))
    print(f"Index: {i} {pk8}")