import json
from app import RESOURCE_PATH
from pla.core import BASE_ROLLS, generate_from_seed, get_rolls, get_sprite
from pla.data import pokedex, natures
from pla.rng import XOROSHIRO

encounter_table = json.load(open(RESOURCE_PATH + "resources/multi-es.json"))

SPAWNER_PTR = "[[main+42a6ee0]+330]"

def multi(group_seed, research, group_id, maxspawns, maxdepth, rolls_override = None):
    rng = XOROSHIRO(group_seed)
    spawns = []
    
    encounters, encsum = precompute(research, group_id, rolls_override)
    
    # init spawns
    for i in range(maxspawns):
        res = generate_spawn2(rng, encounters, encsum, [])
        spawns.append(res)
    
    current = [spawns[-1]]
    for _ in range(maxdepth):
        last = current
        current = []
        
        for pkm in last:
            rng.reseed(pkm['nextseed'])
            for i in range(maxspawns):
                res = generate_spawn2(rng, encounters, encsum, pkm['path'] + [i+1])
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

def check_multi_spawner(reader, research, group_id, maxspawns, maxdepth, isnight, rolls_override = None):
    spawner_pointer = f"{SPAWNER_PTR}+{0x70 + group_id*0x440 + 0x20:X}"
    print(f"Spawner Pointer: {spawner_pointer}")

    generator_seed = reader.read_pointer_int(spawner_pointer, 8)
    group_seed = (generator_seed - 0x82A2B175229D6A5B) & 0xFFFFFFFFFFFFFFFF

    return check_multi_spawner_seed(group_seed, research, group_id, maxspawns, maxdepth, isnight, rolls_override)

def check_multi_spawner_seed(group_seed, research, group_id, maxspawns, maxdepth, isnight, rolls_override = None):
    if isnight and encounter_table.get(f"{group_id}"+"n") is not None:
        print("Night check is ok")
        group_id = f"{group_id}" + "n"
        print(f"Group ID: {group_id}")
    
    return multi(group_seed, research, group_id, maxspawns, maxdepth, rolls_override)
    