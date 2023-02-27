import math

def setPID(high, low):
    return (high << 16) | low

def setIVs(iv1, iv2):
    ivs = [0,0,0,0,0,0]

    ivs[0] = iv1 & 0x1f
    ivs[1] = (iv1 >> 5) & 0x1f
    ivs[2] = (iv1 >> 10) & 0x1f
    ivs[3] = (iv2 >> 5) & 0x1f
    ivs[4] = (iv2 >> 10) & 0x1f
    ivs[5] = iv2 & 0x1f

    return ivs

def setShiny(tsv, psv):

    if tsv == psv:
        return True,True
    elif (tsv ^ psv) < 8:
        return True,False
    else:
        return False,False

def calcHiddenPower(ivs):
    order = [0,1,2,5,3,4]

    h = 0
    p = 0

    for i in range(0,6):
        h += (ivs[order[i]] & 1) << i
        p += ((ivs[order[i]] >> 1) & 1) << i
    
    hidden = math.floor(h * 15 / 63)
    power = math.floor(30 + (p * 40 / 63))

    return hidden,power