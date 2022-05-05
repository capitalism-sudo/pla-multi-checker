from pla.data.pokedex import DexEntry

BASE_ROLLS = 1
BASE_ROLLS_OUTBREAKS = 26
BASE_ROLLS_MMOS = 13

def get_rolls(pokemon: DexEntry, research, base_level):
    rolls = base_level
    
    if research['shinycharm']:
        rolls += 3
    
    if pokemon.species in research['rolls']:
        rolls += research['rolls'][pokemon.species]
    else:
        print(f"No research found for {pokemon.species}")
    
    return rolls