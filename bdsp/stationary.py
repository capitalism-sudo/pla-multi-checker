from bdsp.core import generate_stationary
from bdsp.core.generate_bdsp import generate_stationary
from pla.rng import Xorshift
from app import RESOURCE_PATH
from pla.data import natures
from bdsp.filters import compare_all_ivs
from pla.core import get_bdsp_sprite

with open(RESOURCE_PATH + "resources/text_species_en.txt",encoding="utf-8") as text_species:
    SPECIES = text_species.read().split("\n")

def read_stationary_seed(states,filter,fixed_ivs=0,set_gender=False,species=0,delay=0):

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
    
    for i in range(filter['maxadv']-filter['minadv']+1):
        rng_copy = Xorshift(*rng.current().copy())

        ec,pid,shiny,square,ivs,ability,gender,nature = generate_stationary(rng_copy, set_gender, 3 if fixed_ivs else 0)

        info = {
            "shiny": shiny,
            "square": square,
            "ec": ec,
            "pid": pid,
            "ivs": ivs,
            "ability": ability,
            "gender": gender,
            "nature": natures(nature),
            "adv": i + filter['minadv'],
            "sprite": get_bdsp_sprite(species, shiny),
            "species": SPECIES[species]
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
        rng.alt_next()

    return result