# Go to root of PyNXReader
import sys
from .xoroshiro import XOROSHIRO

with open("./static/resources/text_natures.txt",encoding="utf-8") as text_natures:
    NATURES = text_natures.read().split("\n")

def generate_from_seed(seed,rolls,guaranteed_ivs=0,set_gender=False):
    rng = XOROSHIRO(seed)
    ec = rng.rand(0xFFFFFFFF)
    sidtid = rng.rand(0xFFFFFFFF)
    for _ in range(rolls):
        pid = rng.rand(0xFFFFFFFF)
        shiny = ((pid >> 16) ^ (sidtid >> 16) \
            ^ (pid & 0xFFFF) ^ (sidtid & 0xFFFF)) < 0x10
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
    if set_gender:
        gender = -1
    else:
        gender = rng.rand(252) + 1
    nature = rng.rand(25)
    return ec,pid,ivs,ability,gender,nature,shiny

def check_alpha_from_seed(group_seed,rolls,isalpha,set_gender):
    print(f"Rolls: {rolls} Is Alpha? {isalpha} Set Gender? {set_gender}")
    guaranteed_ivs = 3 if isalpha else 0
    main_rng = XOROSHIRO(int(group_seed))
    adv = -1
    while True:
        adv += 1
        rng = XOROSHIRO(*main_rng.seed.copy())
        spawner_seed = rng.next()
        rng = XOROSHIRO(spawner_seed)
        rng.next()
        fixed_seed = rng.next()
        ec,pid,ivs,ability,gender,nature,shiny = \
            generate_from_seed(fixed_seed,rolls,guaranteed_ivs,set_gender)
        if shiny:
            break
        main_rng.next()
        main_rng.next()
        main_rng = XOROSHIRO(main_rng.next())

    results = {
        "spawn": True,
        "adv": adv,
        "ivs": ivs,
        "gender": gender,
        "nature": NATURES[nature]
        }

    return results


