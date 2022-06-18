from pla.rng import Xorshift,XOROSHIRO_BDSP
from .daycare import Daycare
from pla.data import natures

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

def generate_egg(rng: Xorshift, info: Daycare):

    seed = rng.alt_next()
    displayseed = seed
    
    if (seed & 0x80000000):
        seed |= 0xffffffff00000000

    egg_rng = XOROSHIRO_BDSP(seed)


    if info.is_nido_volbeat():
        egg_rng.next()
    
    
    #genderatio stuff

    ratio = info.get_gender_ratio()


    if ratio == 255:
        gender = 2
    elif ratio == 254:
        gender = 1
    elif ratio == 0:
        gender = 0
    else:
        gender_rand = egg_rng.rand(252) + 1
        if gender_rand < ratio:
            gender = 1
        else:
            gender = 0


    #nature

    nature = egg_rng.rand(25)
    nature = natures(nature)


    if info.get_everstone_count() == 2:
        nature = info.get_parent_nature(egg_rng.rand(2))
    elif info.get_parent_item(0) == 1:
        nature = info.get_parent_nature(0)
    elif info.get_parent_item(1) == 1:
        nature = info.get_parent_nature(1)

    #ability
    
    parentAbility = info.get_parent_ability(0 if info.is_ditto(1) else 1)
    ability = egg_rng.rand(100)

    if parentAbility == 2:
        if ability < 20:
            ability = 0
        elif ability < 40:
            ability = 1
        else:
            ability = 2
    elif parentAbility == 1:
        ability = 0 if ability < 20 else 1
    else:
        ability = 0 if ability < 80 else 1

    #ivs
    
    ivs = [-1,-1,-1,-1,-1,-1]

    inherit = info.get_inherit()

    for _ in range(0,inherit):
        index = egg_rng.rand(6)
        while ivs[index] != -1:
            index =  egg_rng.rand(6)
        p_inherit =  egg_rng.rand(2)
        ivs[index] = info.get_parent_iv(index, p_inherit)
    
    for i in range(6):
        iv = egg_rng.rand(32)
        if ivs[i] == -1:
            ivs[i] = iv

    ec = egg_rng.next()

    pid = 0
    shinyval = 0

    for i in range(info.get_pidrolls()):
        pid = egg_rng.rand(0xffffffff)
        tid = info.get_tid()
        sid = info.get_sid()

        shinyval = ((pid >> 16) ^ (sid & 0xFFFF) \
            ^ (pid & 0xFFFF) ^ (tid & 0xFFFF))

        if shinyval < 0x10:
            break
    
    if shinyval == 0 and pid != 0:
        square = True
        shiny = True
    elif shinyval < 0x10 and pid != 0:
        shiny = True
        square = False
    else:
        shiny = False
        square = False

    return nature, ability, ivs, ec, pid, shiny, square, gender, displayseed