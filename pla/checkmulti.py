import json
from app import RESOURCE_PATH
from pla.core import BASE_ROLLS, generate_from_seed, get_rolls, get_sprite
from pla.data import pokedex, natures
from pla.rng import XOROSHIRO

encounter_table = json.load(open(RESOURCE_PATH + "resources/multi-es.json"))

SPAWNER_PTR = "[[main+42a6ee0]+330]"

def multi(group_seed, research, group_id, maxspawns, minspawns, maxdepth, initspawns, is_variable, rolls_override = None, maxalive_seed = 0):
    rng = XOROSHIRO(group_seed)
    spawns = []
    
    encounters, encsum = precompute(research, group_id, rolls_override)
    
    # init spawns
    if  not is_variable:
        roundspawns = maxspawns
        initspawns = maxspawns
        initnextspawns = initspawns
    else:
        #seed = (maxalive_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF
        #_,roundspawns = get_current_spawns(seed, maxspawns, minspawns)
        maxalive_seed,initnextspawns = get_current_spawns(maxalive_seed, maxspawns, minspawns)
        roundspawns = initspawns
        #print(f"Seed: {seed:X}")
        print(f"Maxalive Seed: {maxalive_seed:X}")
    
    print(f"Initial Round Spawns: {roundspawns}")
    for i in range(roundspawns):
        res = generate_spawn2(rng, encounters, encsum, [])
        res["nextspawns"] = initnextspawns
        spawns.append(res)
    
    roundspawns = initnextspawns
    current = [spawns[-1]]
    for adv in range(maxdepth):
        last = current
        current = []

        if not is_variable:
            roundspawns = maxspawns
            currspawns = maxspawns
            delta = 0
        else:
            currspawns = roundspawns
            maxalive_seed,roundspawns = get_current_spawns(maxalive_seed, maxspawns, minspawns)
            delta = roundspawns - currspawns
            print(f"Delta: {delta}")
            for pkmn in last:
                rng.reseed(pkmn['nextseed'])
                for i in range(delta):
                    res = generate_spawn2(rng, encounters, encsum, pkmn['path'] + [i+1])
                    res["nextspawns"] = roundspawns
                    current.append(res)
                    spawns.append(res)
            if delta <= 0:
                delta = 0

        print(f"Round spawns for Advance {adv+1}: {currspawns}")
        print(f"Next Round Spawns: {roundspawns}")
        print(f"Next Maxalive Seed: {maxalive_seed:X}")
        
        for pkm in last:
            rng.reseed(pkm['nextseed'])
            if delta != 0:
                rng.next()
                rng.next()
                rng.reseed(*rng.seed)
            for i in range(delta,currspawns):
                res = generate_spawn2(rng, encounters, encsum, pkm['path'] + [i+1])
                res["nextspawns"] = roundspawns
                current.append(res)
                spawns.append(res)
    
    return spawns

def generate_spawn2(rng, encounters, encsum, path):
    gen_seed = rng.next()
    rng.next()
    
    fixed_rng = XOROSHIRO(gen_seed)
    encvalue = fixed_rng.next() / (2**64)
    encounter_slot = encvalue * encsum
    
    for e in encounters:
        if encounter_slot < e['slotsum']:
            enc = e
            break
    
    fixed_seed = fixed_rng.next()

    ec,pid,ivs,ability,gender,nature,shiny,square = \
        generate_from_seed(fixed_seed, enc['rolls'], enc['guaranteed_ivs'], enc['fixed_gender'])
    gender = enc['pokemon'].calculate_gender(gender)
    
    rngstate = rng.seed
    nextseed = rng.next()
    rng.reseed(*rngstate)

    return {
        "path": path,
        "ec": ec,
        "pid": pid,
        "ivs": ivs,
        "ability": ability,
        "gender": gender.value,
        "nature": natures(nature),
        "shiny": shiny,
        "square": square,
        "species": enc['pokemon'].display_name(),
        "sprite": get_sprite(enc['pokemon'], shiny, gender),
        "alpha": enc['alpha'],
        "rolls": enc['rolls'],
        "encvalue": encvalue,
        "nextseed": nextseed 
    }

def precompute(research, group_id, rolls_override = None):
    enctable = encounter_table[str(group_id)]
    encsum = sum(e['slot'] for e in enctable)
    
    cache = []
    slotsum = 0
    
    for slot in enctable:
        slotsum += slot['slot']
        pokemon = pokedex.entry(slot['species'])
        cache.append({
            'slotsum': slotsum,
            'pokemon': pokemon,
            'alpha': slot['alpha'],
            'guaranteed_ivs': 3 if slot['alpha'] else 0,
            'rolls': rolls_override if rolls_override is not None else get_rolls(pokemon, research, BASE_ROLLS),
            'fixed_gender': pokemon.is_fixed_gender() or pokemon.id == 'Basculin-2'
        })
        
    return cache, encsum

def get_current_spawns(seed,maxalive,minalive):
    rng = XOROSHIRO(seed)
    delta = maxalive - minalive
    roundalive = minalive + rng.rand(delta+1)
    #print(f"Seed after generating Round: {rng.next():X}")
    #rng.reseed(rng.next())

    return rng.next(),roundalive

def check_multi_spawner(reader, research, group_id, maxspawns, maxdepth, isnight, minspawns, initspawns, is_variable, rolls_override = None):
    spawner_pointer = f"{SPAWNER_PTR}+{0x70 + group_id*0x440 + 0x20:X}"
    print(f"Spawner Pointer: {spawner_pointer}")

    generator_seed = reader.read_pointer_int(spawner_pointer, 8)
    group_seed = (generator_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF

    minspawns = 2

    maxalive_seed = reader.read_pointer_int(f"{SPAWNER_PTR}+{0x70 + group_id*0x440 + 0x400:X}",8)
    #maxalive_seed = reader.read_pointer_int(f"{SPAWNER_PTR}+{0x70 + group_id*0x440 + 0x20 - 0x50:X}",8)
    #maxalive_seed = (maxalive_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF
    print(f"Maxalive Seed Pointer: {SPAWNER_PTR}+{0x70 + group_id*0x440 + 0x400:X}")
    #print(f"Maxalive Seed Pointer: {SPAWNER_PTR}+{0x70 + group_id*0x440 + 0x20 - 0x50:X}")

    return check_multi_spawner_seed(group_seed, research, group_id, maxspawns, minspawns, maxdepth, isnight, initspawns, is_variable, rolls_override, maxalive_seed)

def check_multi_spawner_seed(group_seed, research, group_id, maxspawns, minspawns, maxdepth, isnight, initspawns, is_variable, rolls_override = None, maxalive_seed = 0):
    if isnight and encounter_table.get(f"{group_id}"+"n") is not None:
        print("Night check is ok")
        group_id = f"{group_id}" + "n"
        print(f"Group ID: {group_id}")
    
    return multi(group_seed, research, group_id, maxspawns, minspawns, maxdepth, initspawns, is_variable, rolls_override, maxalive_seed)
    