from bdsp.core import generate_egg
from bdsp.core.generate_bdsp import generate_egg
from pla.rng import Xorshift
from pla.data import natures
from bdsp.filters import compare_all_ivs
from bdsp.core import Daycare

def read_egg_seed(states, filter, daycare_info, delay):

    daycare = Daycare(**daycare_info)

    result = {}

    for i in range(4):
        states[i] = int(states[i],16)

    rng = Xorshift(*states)

    #advance for delay

    for _ in range(delay):
        rng.alt_next()

    #advance to minimum adv

    for _ in range(filter['minadv']):
        rng.alt_next()

    compat = daycare.get_compatibility()

    for i in range(filter['maxadv']-filter['minadv']+1):
        rng_copy = Xorshift(*rng.current().copy())
        rng.alt_next()

        if rng_copy.alt_rand(100) < compat:

            nature, ability, ivs, ec, pid, shiny, square, gender, seed = generate_egg(rng_copy, daycare)

            info = {
                "nature": nature,
                "ability": ability,
                "ivs": ivs,
                "ec": ec,
                "pid": pid,
                "shiny": shiny,
                "square": square,
                "gender": gender,
                "seed": seed,
                "adv": i + filter['minadv']
            }

            #filter out based on IVs

            """
            for i in range(6):
                if filter['minivs'][i] == '':
                    filter['minivs'][i] = 0

            for i in range(6):
                if filter['maxivs'][i] == '':
                    filter['maxivs'][i] = 0
            """

            if compare_all_ivs(filter['minivs'], filter['maxivs'], ivs):
                result[i] = info
    
    return result
