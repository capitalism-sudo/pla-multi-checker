import bdsp_ug_generator_py
import pandas
import sys
sys.path.append('../')
#from pla.data.pokedex import Pokedex
from pla.data import pokedex
from pla.data import natures

def main():

    #print(bdsp_ug_generator_py.generate_results(10000, [0x0cf67c48, 0x52b2e5cd, 0x1dbfee6b, 0xf212d747], 2, 6, "SpaciousCave", True))
    result = bdsp_ug_generator_py.generate_results(10000, 0x0cf67c48, 0x52b2e5cd, 0x1dbfee6b, 0xf212d747, 2, 6, 2, False)

    #pkdex = Pokedex()
    #dex = pkdex.nationaldex()
    print("Attempting to print results")
    #rare = result[0].rare_pokemon
    print("Results:")
    #normal = result[0].regular_pokemon

    for i,value in enumerate(result):
        normal = value.regular_pokemon
        rare = value.rare_pokemon
        for p, norm in enumerate(normal):
            if(norm.shiny):
                print(f"Pokemon {p}")
                pokemon = pokedex.entry_by_dex(norm.species)
                print(f"Advance {i}")
                print(f"EC: {norm.ec:X} PID: {norm.pid:X} Species: {pokemon.display_name()}")
                print(f"IVS: {norm.ivs}")
                print(f"Nature: {natures(norm.nature)}")
        if rare is not None:
            if(rare.shiny):
                print(f"Rare Pokemon 1")
                print(f"Advance {i}")
                pokemon = pokedex.entry_by_dex(rare.species)
                print(f"EC: {rare.ec:X} PID: {rare.pid:X} Species: {pokemon.display_name()}")
                print(f"IVS: {rare.ivs}")
                print(f"Nature: {natures(rare.nature)}")


    
    
if __name__ == "__main__":
    main()