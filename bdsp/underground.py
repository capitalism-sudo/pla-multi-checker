import json
import struct
import sys
from .bdsp_ug_generator_py import generate_results, FilterPy
from app import RESOURCE_PATH
from pla.data import natures
from pla.core import get_bdsp_sprite
from bdsp.filters import compare_all_ivs

with open(RESOURCE_PATH + "resources/text_species_en.txt",encoding="utf-8") as text_species:
    SPECIES = text_species.read().split("\n")

with open(RESOURCE_PATH + "resources/moves_en.txt",encoding="utf-8") as text_moves:
    MOVES = text_moves.read().split("\n")

def shiny_check(result):
    normal = result.regular_pokemon
    rare = result.rare_pokemon
    for i, value in enumerate(normal):
        if value.shiny:
            return True
    if rare is None:
        return False
    if rare.shiny:
        return True
    
    return False

def check_ug_advance(s0,s1,s2,s3,story_flag,room,version,advances,minadvances,diglett,ivfilter):

    filter = FilterPy(False, None, [0,0,0,0,0,0], [31,31,31,31,31,31], None, None, None, None, None)
    results = generate_results(advances, [int(s0,16),int(s1,16),int(s2,16),int(s3,16)], version, story_flag, room, filter, diglett)
    final = {}

    for i, result in enumerate(results):
        full = []
        norm = result.regular_pokemon
        rare = result.rare_pokemon
        advance = result.advance
        if advance >= minadvances:
            for z, mon in enumerate(norm):
                monster = {
                    "ec": f"{mon.ec:X}",
                    "pid": f"{mon.pid:X}",
                    "ivs": mon.ivs,
                    "nature": natures(mon.nature),
                    "ability": mon.ability,
                    "gender": mon.gender,
                    "species": SPECIES[mon.species],
                    "eggmove": MOVES[mon.egg_move] if mon.egg_move is not None else "None",
                    "shiny": mon.shiny,
                    "sprite": get_bdsp_sprite(mon.species, mon.shiny),
                    "spawn": f"Spawn {z+1}",
                    "advances": advance,
                    "rarespawn": False
                }
                if compare_all_ivs(ivfilter['minivs'], ivfilter['maxivs'], monster['ivs']):
                    full.append(monster)
            if rare is not None:
                monster = {
                    "ec": f"{rare.ec:X}",
                    "pid": f"{rare.pid:X}",
                    "ivs": rare.ivs,
                    "nature": natures(rare.nature),
                    "ability": rare.ability,
                    "gender": rare.gender,
                    "species": SPECIES[rare.species],
                    "eggmove": MOVES[rare.egg_move] if rare.egg_move is not None else "None",
                    "shiny": rare.shiny,
                    "sprite": get_bdsp_sprite(rare.species, rare.shiny),
                    "spawn": "Rare",
                    "advances": advance,
                    "rarespawn": True
                }
                if compare_all_ivs(ivfilter['minivs'], ivfilter['maxivs'], monster['ivs']):
                    full.append(monster)
            final[str(i)] = full

    return final

"""
if __name__ == "__main__":
    check_ug_advance(0x0cf67c48, 0x52b2e5cd, 0x1dbfee6b, 0xf212d747,6,2,2,10000,False)

    #10000, 0x0cf67c48, 0x52b2e5cd, 0x1dbfee6b, 0xf212d747, 2, 6, 2, False
"""