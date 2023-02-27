import numpy as np
from numba_pokemon_prngs.lcrng import PokeRNGDiv

#imports from main.py
from gen3.core import *
from gen3.filters import compare_all_ivs
from gen3.data import natures, pktype


'''
imports running as test
from core import *
from filters import compare_all_ivs
from data import natures, pktype
'''

def check_statics(tid,sid,filter,delay,method=1,seed=0):
    result = {}

    seed = int(seed,16)
    tid = int(tid)
    sid = int(sid)

    minadv = filter['minadv']
    maxadv = filter['maxadv']

    tsv = (tid ^ sid)

    init = PokeRNGDiv(seed)
    init.advance(minadv+delay)

    for i in range(0,maxadv+1):
    
        rng = PokeRNGDiv(init.seed)
        #print(f"Seed: {rng.seed:0X}")

        low = rng.next_u16()
        high = rng.next_u16()

        if method == 2:
            rng.next()
        
        iv1 = rng.next_u16()

        if method == 4:
            rng.next()
        
        iv2 = rng.next_u16()

        pid = setPID(high,low)
        ability = low & 1
        nature = pid % 25
        psv = high ^ low
        shiny,square = setShiny(tsv, high ^ low)
        gender = low & 255

        ivs = setIVs(iv1,iv2)
        hidden,power = calcHiddenPower(ivs)

        info = {
            "shiny":shiny,
            "square":square,
            "pid": pid,
            "ivs":ivs,
            "ability":ability,
            "nature":natures(nature),
            "adv": i + minadv,
            "hidden": pktype(hidden),
            "power": power,
            "psv": psv,
            "high": int(high),
            "low": int(low),
            "gender": gender
        }

        if compare_all_ivs(filter['minivs'], filter['maxivs'], ivs):
            result[i] = info
        
        init.next()

    return result


if __name__ == '__main__':
    seed = 0xe38464fb
    tid = 11111
    sid = 21150

    filter = {
        "minivs": [0,0,0,0,0,0],
        "maxivs": [31,31,31,31,31,31]
    }

    result = check_statics(tid,sid,0,100000,0,filter,1,seed)

    for _,res in result.items():
        if res['shiny']:
            print(f"Advance: {res['adv']} PID: {res['pid']:X} Shiny: {'Square' if res['square'] else 'True' if res['shiny'] else 'False'} " + \
                f"Nature: {res['nature']} Ability: {res['ability']} IVs: {res['ivs']} Hidden: {res['hidden']} Power: {res['power']}")
    #print(result)