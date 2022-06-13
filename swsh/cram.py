from pla.rng import XOROSHIRO

def filt(result, filter):
    if filter['isSafariSport'] and not result['isSafariSport']:
        return False
    elif filter['isBonusCount'] and not result['isBonusCount']:
        return False
    else:
        return True

def generate(_rng: XOROSHIRO, npc_count = 21):
    __rng = XOROSHIRO(*_rng.seed.copy())
    #menu close advances
    menu_advances = 0

    
    for _ in range(npc_count):
        menu_advances += __rng.rand_count(91)[1]
    __rng.next()
    menu_advances += 1
    menu_advances += __rng.rand_count(91)[1]


    #Jam the Cram

    item_roll = __rng.rand(4)
    ball_roll = __rng.rand(100)
    is_safari_sport = __rng.rand(1000) == 0
    if is_safari_sport or ball_roll == 99:
        is_bonus_count = __rng.rand(1000) == 0
    else:
        is_bonus_count = __rng.rand(100) == 0

    return {"menuAdvances": menu_advances, "itemRoll": item_roll, "ballRoll": ball_roll, "isSafariSport": is_safari_sport, "isBonusCount": is_bonus_count}

def predict_cram(seed_s0, seed_s1, npc_count, filter):
    rng = XOROSHIRO(int(seed_s0, 16), int(seed_s1, 16))
    predict = XOROSHIRO(int(seed_s0, 16), int(seed_s1, 16))

    advances = -1

    predict_advances = 0

    print(f"State {rng.state:016x}")
    print(f"isSafariSport Filter: {filter['isSafariSport']}, isBonusCount Filter: {filter['isBonusCount']}")
    print("Finding Target...")

    result = generate(predict, npc_count)

    #print(f"State {rng.state:016x}")
    #print("Finding Target...")

    while not filt(result, filter):
        predict_advances += 1
        predict.next()
        result = generate(predict, npc_count)
        #print(f"Predict State: {predict.seed[0]:X}, {predict.seed[1]:X}")
        #print(predict_advances, result)
        #print()
    
    last = 0

    print ("Prediction:")
    print(f"Predict State: {predict.seed[0]:X}, {predict.seed[1]:X}")
    print(predict_advances, result)
    print()

    return { "adv": predict_advances, "sportsafari": result['isSafariSport'], "bonus": result['isBonusCount'], "menu_adv": result['menuAdvances'] }