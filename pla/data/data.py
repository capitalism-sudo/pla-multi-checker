from app import RESOURCE_PATH
from .pokedex import Pokedex

pokedex = Pokedex()
hisuidex = pokedex.hisuidex()

with open(RESOURCE_PATH + "resources/text_natures.txt",encoding="utf-8") as text_natures:
    _natures = text_natures.read().split("\n")

def natures(nature_id):
    return _natures[nature_id]