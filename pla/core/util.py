from typing import Union
from pla.data.gender import Gender
from pla.data.pokedex import DexEntry

# This might not be the best place for these functions, but collecting them here for now
def get_sprite(pokemon: DexEntry, shiny: bool = False, gender: Union[Gender, None] = None):
    form_flag = '' if pokemon.is_base_form() else '-' + pokemon.form_id
    gender_flag = 'f' if pokemon.is_gender_dimorphic and gender == Gender.FEMALE else ''
    shiny_flag = 's' if shiny else ''
    return f"c_{pokemon.dex_number()}{form_flag}{gender_flag}{shiny_flag}.png"
    
def get_bdsp_sprite(species, shiny: bool = False):
    form_flag = ''
    gender_flag = ''
    shiny_flag = 's' if shiny else ''
    return f"c_{species}{form_flag}{gender_flag}{shiny_flag}.png"