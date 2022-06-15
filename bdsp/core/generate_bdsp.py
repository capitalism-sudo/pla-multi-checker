from pla.rng import Xorshift

def generate_stationary(rng:Xorshift, fixed_gender=False, guaranteed_ivs=0):

    ec = rng.alt_next()
    shiny_alt_rand = rng.alt_next()
    pid = rng.alt_next()

    psv = shiny_alt_rand & 0xFFFF ^ shiny_alt_rand >> 0x10
    tsv = pid >> 0x10 ^ pid & 0xFFFF

    if (psv ^ tsv) < 0x10:
        if (psv ^ tsv) == 0:
            shiny = True
            square = True
        else:
            shiny = True
            square = False
    else:
        shiny = False
        square = False

    ivs = [-1,-1,-1,-1,-1,-1]

    
    for _ in range(0,guaranteed_ivs):
        index = rng.alt_rand(6)
        while ivs[index] != -1:
            index = rng.alt_rand(6)
        ivs[index] = 31

    for i in range(6):
        if ivs[i] == -1:
            ivs[i] = rng.alt_rand(32)
    
    ability = rng.alt_rand(2)

    gender = -1 if fixed_gender else rng.alt_rand(252)+1
    nature = rng.alt_rand(25)

    return ec,pid,shiny,square,ivs,ability,gender,nature