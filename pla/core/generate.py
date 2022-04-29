from pla.rng import XOROSHIRO

def generate_from_seed(seed, rolls, guaranteed_ivs=0, fixed_gender=False):
    rng = XOROSHIRO(seed)
    ec = rng.rand(0xFFFFFFFF)
    sidtid = rng.rand(0xFFFFFFFF)
    
    for _ in range(rolls):
        pid = rng.rand(0xFFFFFFFF)
        shinyval = ((pid >> 16) ^ (sidtid >> 16) \
            ^ (pid & 0xFFFF) ^ (sidtid & 0xFFFF))
        shiny = shinyval < 0x10
        square = shinyval == 0x0
        if shiny:
            break
    
    ivs = [-1,-1,-1,-1,-1,-1]
    for i in range(guaranteed_ivs):
        index = rng.rand(6)
        while ivs[index] != -1:
            index = rng.rand(6)
        ivs[index] = 31
    
    for i in range(6):
        if ivs[i] == -1:
            ivs[i] = rng.rand(32)
    
    ability = rng.rand(2) # rand(3) if ha possible
    gender = -1 if fixed_gender else rng.rand(252) + 1
    nature = rng.rand(25)
    
    return ec, pid, ivs, ability, gender, nature, shiny, square