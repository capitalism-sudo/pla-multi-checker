import numpy as np
RESOURCE_PATH = './static/'
from enum import Enum
import struct
import bz2
import os

class Gender(Enum):
    GRASS = 1,
    DOUBLEGRASS = 2,
    SPECIALGRASS = 3,
    ROCKSMASH = 4,
    SURFING = 5,
    SPECIALSURF = 6,
    OLDROD = 7,
    GOODROD = 8,
    SUPERROD = 9,
    SPECIALSUPERROD = 10,
    STATIC = 11,
    BUGCATCHINGCONTEST = 12,
    HEADBUTT = 13,
    ROAMER = 14,
    GIFT = 15,
    ENTRALINK = 16,
    GIFTEGG = 17,
    HIDDENGROTTO = 18

encounter = open(RESOURCE_PATH + "resources/emerald.bin", mode='rb')

with open(RESOURCE_PATH + "resources/emerald.bin", mode='rb') as f:
    data = f.read()

arrays = []

size = len(data)
data = bz2.compress(data,9)
data = size.to_bytes(2, byteorder="little") + data

name = os.path.basename(f.name).replace(".bin", "")
string = f"constexpr std:array<u8, {len(data)}> {name} = {{ "

for i in range(len(data)):
    string += str(data[i])
    if i != len(data) - 1:
        string += ", "

string += " };"
arrays.append(string)

print(arrays)
