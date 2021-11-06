# Go to root of PyNXReader
import signal
import sys
import json

sys.path.append('../')

from nxreader import SWSHReader
from rng import XOROSHIRO

tsv = 61257^1240 # tid^sid
shiny_charm = True
mark_charm = True
weather = True
fishing = False

personality_marks = ["Rowdy","AbsentMinded","Jittery","Excited","Charismatic","Calmness","Intense","ZonedOut","Joyful","Angry","Smiley","Teary","Upbeat","Peeved","Intellectual","Ferocious","Crafty","Scowling","Kindly","Flustered","PumpedUp","ZeroEnergy","Prideful","Unsure","Humble","Thorny","Vigor","Slump"]
natures = ["Hardy","Lonely","Brave","Adamant","Naughty","Bold","Docile","Relaxed","Impish","Lax","Timid","Hasty","Serious","Jolly","Naive","Modest","Mild","Quiet","Bashful","Rash","Calm","Gentle","Sassy","Careful","Quirky"]

config = json.load(open("../config.json"))
r = SWSHReader(config["IP"])

def signal_handler(signal, frame): #CTRL+C handler
    print("Stop request")
    r.close()

signal.signal(signal.SIGINT, signal_handler)
rng = XOROSHIRO(int.from_bytes(r.read(0x4C2AAC18,8),"little"),int.from_bytes(r.read(0x4C2AAC18+8,8),"little"))
predict = XOROSHIRO(*rng.seed.copy())
target = -1
advances = 0

# generate from current state
def generate(rng):
    seed = rng.state()
    go = XOROSHIRO(*rng.seed)
    go.next() # one of below?
    # not used for strong spawns
    # slotChoice(??? rolls, different branches for encounter types & KO stuff)
    # getRandomForm (if 31, defer for later; only roll rand(0,8) for minor)
    # getRandomLevel = min + rand(max-min); only roll if min != max
    # boostLevelTo60 if appropriate (overwriting the random level)
    # rand(1000) brilliant proc, consider the amount defeated
    for roll in range(3 if shiny_charm else 1): # u32 shiny; loop for reroll count based on charm and if encounters can exist
        shinyu32 = go.nextuint()
        shiny = (((shinyu32 >> 16) ^ (shinyu32 & 0xFFFF)) ^ tsv)
        if shiny < 16:
            break
    go.rand(2) #-???
    nature = go.rand(25) # -nature
    ability = 0 if go.rand(2) == 1 else 1 # -ability
    # rand(100) ONLY IF both personal held items (Item1, Item2) are different values (a/0 or a/b, not a/a or 0/0)
    # rand(something, probably eggmove count) if brilliant -eggmove
    fixed_seed = go.nextuint() # u32 fixed seed
    temp = XOROSHIRO(fixed_seed)

    ec = temp.nextuint()
    pid = temp.nextuint()
    if not shiny < 16:
        if (((pid >> 16) ^ (pid & 0xFFFF)) ^ tsv) < 16:
            pid ^= 0x10000000
    else:
        if not (((pid >> 16) ^ (pid & 0xFFFF)) ^ tsv) < 16:
            pid = (((tsv ^ (pid & 0xFFFF)) << 16) | (pid & 0xFFFF)) & 0xFFFFFFFF
    shiny = (((pid >> 16) ^ (pid & 0xFFFF)) ^ tsv)

    ivs = [32]*6
    for i in range(0): # 0 set ivs for now
        index = temp.rand(6)
        while ivs[index] != 32:
            index = temp.rand(6)
        ivs[index] = 31
        
    for i in range(6):
        if ivs[i] == 32:
            ivs[i] = temp.rand(32)
        
    mark = "No"
    for roll in range(3 if mark_charm else 1):
        rare_rand = go.rand(1000)
        personality_rand = go.rand(100)
        uncommon_rand = go.rand(50)
        weather_rand = go.rand(50)
        time_rand = go.rand(50)
        fish_rand = go.rand(25)
        if rare_rand == 0:
            mark = "Rare"
            break
        if personality_rand == 0:
            mark = personality_marks[go.rand(len(personality_marks))]
            break
        if uncommon_rand == 0:
            mark = "Uncommon"
            break
        if weather_rand == 0:
            if weather:
                mark = "Weather"
                break
        if time_rand == 0:
            mark = "Time"
            break
        if fish_rand == 0:
            if fishing:
                mark = "Fishing"
                break
    # return f"Main Seed: {seed:016X} Overworld Seed: {fixed_seed:08X} \nShiny: {'Not Shiny' if shiny > 15 else ('Square' if shiny == 0 else 'Star')} Nature: {natures[nature]} Ability: {ability} \nEC: {ec:08X} PID: {pid:08X} \nIVs: {'/'.join(str(iv) for iv in ivs)} \nMark: {mark}"
    return [seed,fixed_seed,shiny,nature,ability,ec,pid,ivs,mark]

# filter for target
def gen_filter(result):
    seed,fixed_seed,shiny,nature,ability,ec,pid,ivs,mark = result
    if mark == "No":
        return False
    if shiny > 15:
        return False
    return True

result = generate(predict)
target += 1
predict.next()
while not gen_filter(result):
    result = generate(predict)
    target += 1
    predict.next()
print(f"Advance {advances}, Target {target}, State {rng.state():016X}")
seed,fixed_seed,shiny,nature,ability,ec,pid,ivs,mark = result
print(shiny)
print(f"{seed:016X},{fixed_seed:08X},{'Not Shiny' if shiny > 15 else ('Square' if shiny == 0 else 'Star')},{natures[nature]},{ability},{ec:08X},{pid:08X},{'/'.join(str(iv) for iv in ivs)},{mark}")
while True:
    read = int.from_bytes(r.read(0x4C2AAC18,16),"little")
    while rng.state() != read:
        rng.next()
        advances += 1
        if rng.state() == read:
            print(f"Advance {advances}, Target {target}, State {rng.state():016X}")
            seed,fixed_seed,shiny,nature,ability,ec,pid,ivs,mark = result
            print(f"{seed:016X},{fixed_seed:08X},{'Not Shiny' if shiny > 15 else ('Square' if shiny == 0 else 'Star')},{natures[nature]},{ability},{ec:08X},{pid:08X},{'/'.join(str(iv) for iv in ivs)},{mark}")
    if advances > target:
        result = generate(predict)
        target += 1
        predict.next()
        while not gen_filter(result):
            result = generate(predict)
            target += 1
            predict.next()