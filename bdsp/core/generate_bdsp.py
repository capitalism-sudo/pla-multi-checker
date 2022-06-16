from pla.rng import Xorshift,XOROSHIRO,XOROSHIRO_BDSP

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

def generate_wild(rng:Xorshift, fixed_gender=False):

    encounter_rand = rng.rand(100)

    rng.advance(84)

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

    for i in range(6):
        if ivs[i] == -1:
            ivs[i] = rng.alt_rand(32)
    
    ability = rng.alt_rand(2)

    gender = -1 if fixed_gender else rng.alt_rand(252)+1
    nature = rng.alt_rand(25)

    encslots = [20,40,50,60,70,80,85,90,94,98,99,100]

    for i,value in enumerate(encslots):
        if encounter_rand < value:
            slot = i
            break

    return ec,pid,shiny,square,ivs,ability,gender,nature,slot

def generate_roamer(rng:Xorshift, fixed_gender=False, guaranteed_ivs=0):

    seed = rng.alt_next()
    ec = seed

    roamer_rng = XOROSHIRO_BDSP(seed)

    shiny_rand = roamer_rng.next()
    pid = roamer_rng.next()

    psv = shiny_rand & 0xFFFF ^ shiny_rand >> 0x10
    tsv = pid >> 0x10 ^ pid & 0xFFFF

    if (psv ^ tsv) < 0x10:
        shiny = True
        square = True if psv ^ tsv == 0 else False
    else:
        shiny = False
        square = False
    
    ivs = [-1,-1,-1,-1,-1,-1]

    for _ in range(0,guaranteed_ivs):
        index = roamer_rng.next() % 6
        while ivs[index] != -1:
            index = roamer_rng.next() % 6
        ivs[index] = 31

    for i in range(6):
        if ivs[i] == -1:
            ivs[i] = roamer_rng.next() % 32
    
    ability = roamer_rng.next() % 1

    if fixed_gender:
        gender = -1
    else:
        gender_rand = roamer_rng.next()
        gender = gender_rand - ((gender_rand / 253) * 253) + 1
    
    nature = roamer_rng.next() % 25

    return ec,pid,shiny,square,ivs,ability,gender,nature

def generate_tid(rng: Xorshift):

    sidtid = rng.alt_next()
    tid = sidtid & 0xFFFF
    sid = sidtid >> 0x10

    tsv = (tid ^ sid) >>  4

    g8tid = sidtid % 1000000

    return tid,sid,tsv,g8tid