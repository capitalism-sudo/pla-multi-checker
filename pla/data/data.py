import json
from app import RESOURCE_PATH
from pla.data.pokedex import Pokedex

with open(RESOURCE_PATH + "resources/text_natures.txt",encoding="utf-8") as text_natures:
    NATURES = text_natures.read().split("\n")

with open(RESOURCE_PATH + "resources/text_species_en.txt", encoding="utf-8") as text_species:
    SPECIES = text_species.read().split("\n")

with open(RESOURCE_PATH + "resources/ratios.json") as json_ratios:
    RATIOS = json.load(json_ratios)

GENDERLESS = ["Porygon", "Porygon2", "Porygon-Z", "Magnemite", "Magneton", "Magnezone", "Bronzor", "Bronzong", "Voltorb", "Electrode", "Rotom", "Unown"]
fixedgenders = ["Porygon", "Porygon2", "Porygon-Z", "Magnemite", "Magneton", "Magnezone", "Happiny", "Chansey", "Blissey", "Petilil", "Lilligant", "Bronzor", "Bronzong", "Voltorb", "Electrode", "Rotom", "Rufflet", "Braviary", "Unown"]

def is_fixed_gender(species):
    return species in fixedgenders

pokedex = Pokedex()
hisuidex = pokedex.hisuidex()

# This can be refactored into a lookup in due course as it will never change
def get_basespecies_form(species):
    form = ""
    if " " in species and "-" in species:
        cutspecies = species.rpartition(' ')[2]
        form = species.rpartition('-')[2]
        cutspecies = cutspecies.rpartition('-')[0]     
    elif " " in species:
        cutspecies = species.rpartition(' ')[2]
    elif "-" in species:
        cutspecies = species.rpartition('-')[0]
        form = species.rpartition('-')[2]
    else:
        cutspecies = species

    return cutspecies, form
