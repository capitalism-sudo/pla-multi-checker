import struct
from pla.core import generate_from_seed
from pla.core.util import get_sprite
from pla.data import SPECIES, NATURES, get_basespecies_form
from pla.rng import XOROSHIRO

from pla.checkmmo import MAX_MAPS, get_group_seed, get_gen_seed_to_group_seed

def get_all_outbreaks(reader, rolls, inmap):
    """reads all normal outbreaks on map"""
    outbreaks = {}
    rolls = rolls + 13

    for map_index in range(MAX_MAPS):
        species,group_seed,max_spawns,coordinates = get_outbreak_info(reader, map_index, inmap)
        
        if species != 0:
            results,_ = pathfind_aggressive_outbreak(group_seed, rolls, max_spawns)
            
            if results is None:
                results = []
            
            for index in results:
                if index not in ('index', 'description'):
                    format_outbreak_result(results[str(index)],species,map_index,max_spawns,coordinates)
            
            outbreaks[f"Outbreak {map_index}"] = results

    return outbreaks

def format_outbreak_result(result,species,map_index,max_spawns,coordinates):
    result["group"] = map_index
    result["mapname"] = "Normal Outbreak"
    result["numspawns"] = max_spawns
    if SPECIES[species] == "Basculin":
        result["species"] = "Basculin-2"
    else:
        result["species"] = SPECIES[species]
    result["coords"] = coordinates

    cutspecies, form = get_basespecies_form(result["species"])
    result["sprite"] = get_sprite(cutspecies, form, result["shiny"])

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
                "generator_seed": f"{generator_seed:X}",
                "shiny": shiny,
                "square": square,
                "alpha": alpha,
                "ec": ec,
                "pid": pid,
                "ivs": ivs,
                "ability": ability,
                "nature": NATURES[nature],
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
                
                storage[str(fixed_seed)] = {
                    "index":f"Path: {'|'.join(str(s) for s in steps[:step_i] + [pokemon])}</span>",
                    "generator_seed": f"{generator_seed:X}",
                    "shiny": shiny,
                    "square": square,
                    "alpha": alpha,
                    "ec": ec,
                    "pid": pid,
                    "ivs": ivs,
                    "ability": ability,
                    "nature": NATURES[nature],
                    "gender": gender,
                    "rolls": rolls,
                    "defaultroute": len(steps[:step_i]) == sum(steps[:step_i]) and pokemon == 1
                }
                paths.append(f"{'|'.join(str(s) for s in steps[:step_i] + [pokemon])}")
        
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
        species,_,_,_ = get_outbreak_info(reader, map_index, inmap)
        if species != 0:
            outbreaks.append(SPECIES[species])

    return outbreaks

def get_outbreak_info(reader, group_id, inmap):
    species = reader.read_pointer_int(f"[[[[[[main+42BA6B0]+2B0]+58]+18]+" \
                                      f"{0x20 + 0x50*group_id:X}", 2)
    
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

    return species, group_seed, max_spawns, coordinates
    