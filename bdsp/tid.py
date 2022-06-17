from .core import generate_tid
from pla.rng import Xorshift


def check_match(filter, result, ids):

    if filter['tid']:
        if result['tid'] not in ids:
            return False
    
    if filter['g8tid']:
        if result['g8tid'] not in ids:
            return False
    
    if filter['sid']:
        if result['sid'] not in ids:
            return False
    
    return True

def read_tid_seed(states, filter, ids):

    result = {}

    if len(ids) != 0:
        ids = ids.split(',')
        for i in range(len(ids)):
            ids[i] = int(ids[i])

    for i in range(4):
        states[i] = int(states[i],16)

    rng = Xorshift(*states)

    for _ in range(filter['minadv']):
        rng.alt_next()

    for i in range(filter['maxadv']-filter['minadv']+1):
        rng_copy = Xorshift(*rng.current().copy())

        tid,sid,tsv,g8tid = generate_tid(rng_copy)

        info = {
            "tid": tid,
            "sid": sid,
            "tsv": tsv,
            "g8tid": g8tid,
            "adv": i + filter['minadv']
        }

        if len(ids) != 0:
            if check_match(filter, info, ids):
                result[i] = info
        else:
            result[i] = info
        
        rng.alt_next()
    
    return result
