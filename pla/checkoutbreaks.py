import struct
from pla.core import BASE_ROLLS_OUTBREAKS, generate_from_seed, get_rolls, get_sprite
from pla.data import pokedex, natures
from pla.rng import XOROSHIRO

from pla.checkmmo import MAX_MAPS, get_group_seed, get_gen_seed_to_group_seed

def get_all_outbreaks(reader, research, inmap, rolls_override = None):
    """reads all normal outbreaks on map"""
    outbreaks = {}

    for map_index in range(MAX_MAPS):
        pokemon, group_seed, max_spawns, coordinates = get_outbreak_info(reader, map_index, inmap)
        
        if pokemon is not None:
            rolls = rolls_override if rolls_override is not None else get_rolls(pokemon, research, BASE_ROLLS_OUTBREAKS)
            results,_ = pathfind_aggressive_outbreak(group_seed, rolls, max_spawns)
            
            if results is None:
                results = []
            
            for result in results.values():
                format_outbreak_result(result, pokemon, map_index, max_spawns, coordinates)
            
            outbreaks[f"Outbreak {map_index}"] = results

    return outbreaks

def format_outbreak_result(result, pokemon, map_index, max_spawns, coordinates):
    result["group"] = map_index
    result["mapname"] = "Normal Outbreak"
    result["numspawns"] = max_spawns
    result["coords"] = coordinates
    
    result["species"] = pokemon.display_name()
    gender = pokemon.calculate_gender(result["gender"])
    result["gender"] = gender.value
    result["sprite"] = get_sprite(pokemon, result["shiny"], gender)

def generate_outbreak_aggressive_path(group_seed, rolls, steps, uniques, paths, storage):
    """Generate all the pokemon of an outbreak based on a provided aggressive path"""
    # pylint: disable=too-many-locals, too-many-arguments
    # the generation is unique to each path, no use in splitting this function
    main_rng = XOROSHIRO(group_seed)
    for init_spawn in range(1,5):
        generator_seed = main_rng.next()
        main_rng.next() # spawner 1's seed, unused
        fixed_rng = XOROSHIRO(generator_seed)
        slot = (fixed_rng.next() / (2**64) * 101)
        alpha = slot >= 100
        fixed_seed = fixed_rng.next()

        if not fixed_seed in uniques:
            uniques.add(fixed_seed)
            ec,pid,ivs,ability,gender,nature,shiny,square = \
                generate_from_seed(fixed_seed, rolls, 3 if alpha else 0)

            storage[str(fixed_seed)] = {
                "index":f"Initial Spawn {init_spawn}</span>",
                "generator_seed": generator_seed,
                "shiny": shiny,
                "square": square,
                "alpha": alpha,
                "ec": ec,
                "pid": pid,
                "ivs": ivs,
                "ability": ability,
                "nature": natures(nature),
                "gender": gender,
                "rolls": rolls,
                "defaultroute": True
            }
    
    group_seed = main_rng.next()
    respawn_rng = XOROSHIRO(group_seed)

    for step_i,step in enumerate(steps):
        for pokemon in range(1,step+1):
            generator_seed = respawn_rng.next()
            respawn_rng.next() # spawner 1's seed, unused
            fixed_rng = XOROSHIRO(generator_seed)
            slot = (fixed_rng.next() / (2**64) * 101)
            alpha = slot >= 100
            fixed_seed = fixed_rng.next()

            if not fixed_seed in uniques:
                uniques.add(fixed_seed)
                ec,pid,ivs,ability,gender,nature,shiny,square = \
                    generate_from_seed(fixed_seed,rolls,3 if alpha else 0)
                path_string = '|'.join(str(s) for s in steps[:step_i] + [pokemon])

                storage[str(fixed_seed)] = {
                    "index":f"Path: {path_string}</span>",
                    "generator_seed": generator_seed,
                    "shiny": shiny,
                    "square": square,
                    "alpha": alpha,
                    "ec": ec,
                    "pid": pid,
                    "ivs": ivs,
                    "ability": ability,
                    "nature": natures(nature),
                    "gender": gender,
                    "rolls": rolls,
                    "defaultroute": len(steps[:step_i]) == sum(steps[:step_i]) and pokemon == 1
                }
                paths.append(path_string)
        
        respawn_rng = XOROSHIRO(respawn_rng.next())

def pathfind_aggressive_outbreak(group_seed,rolls,spawns,step=0,steps=None,uniques=None,paths=None,storage=None):
    """Recursively pathfind to possible shinies for the current outbreak via multi battles"""
    # pylint: disable=too-many-arguments
    # can this algo be improved?
    if steps is None or uniques is None or storage is None or paths is None:
        steps = []
        uniques = set()
        storage = {}
        paths = []
    _steps = steps.copy()
    
    if step != 0:
        _steps.append(step)
    
    if sum(_steps) + step < spawns - 4:
        for _step in range(1, min(5, (spawns - 4) - sum(_steps))):
            if pathfind_aggressive_outbreak(group_seed,rolls,spawns,_step,_steps,uniques,paths,storage) is not None:
                return storage,paths
    else:
        _steps.append(spawns - sum(_steps) - 4)
        generate_outbreak_aggressive_path(group_seed,rolls,_steps,uniques,paths,storage)
        if _steps == get_final_outbreak(spawns):
            return storage,paths
    
    return None

def get_final_outbreak(spawns):
    """Get the final path that will be generated to know when to stop aggressive recursion"""
    spawns -= 4
    path = [4] * (spawns // 4)
    if spawns % 4 != 0:
        path.append(spawns % 4)
    return path

def get_all_outbreak_names(reader, inmap):
    """gets all map names of outbreak locations"""
    outbreaks = []
    for map_index in range(MAX_MAPS):
        pokemon,_,_,_ = get_outbreak_info(reader, map_index, inmap)
        if pokemon is not None:
            outbreaks.append(pokemon.display_name())

    return outbreaks

def get_outbreak_info(reader, group_id, inmap):
    species_index = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                            f"{0x20 + 0x50*group_id:X}", 2)
    if species_index == 0:
        return None, 0, 0, None
    
    group_seed = get_gen_seed_to_group_seed(reader,group_id) if inmap else get_group_seed(reader,group_id,0)
    
    max_spawns = reader.read_pointer_int(f"[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                         f"{0x20 + 0x50*group_id + 0x40:X}", 8)

    coords = struct.unpack('fff',reader.read_pointer(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                                     f"{0x20 + 0x50*group_id + 0x20:X}", 12))

    coordinates = {
        "x":coords[0],
        "y":coords[1],
        "z":coords[2]
    }

    return pokedex.entry_by_index(species_index), group_seed, max_spawns, coordinates
    