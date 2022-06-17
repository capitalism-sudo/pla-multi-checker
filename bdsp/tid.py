from .core import generate_tid
from pla.rng import Xorshift

filtertype = {
    "-1": None,
    "0": "g8tid",
    "1": "tid",
    "2": "sid",
    "3": "tsv"
}
def check_match(filter_type, result, ids):

    if filter_type is not None:
        return result[filter_type] in ids
    
    return True

def read_tid_seed(states, filter, ids):

    result = {}

    filter_type = filtertype[filter['idfilter']]

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

        if check_match(filter_type, info, ids):
            result[i] = info
        
        rng.alt_next()
    
    return result
