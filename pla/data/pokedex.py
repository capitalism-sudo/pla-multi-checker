import json
from app import RESOURCE_PATH

class Pokedex():
    def __init__(self):
        # Three indexes
        self._species = {}
        self._dex = {}
        self._dex['national'] = {}

        with open(RESOURCE_PATH + '/resources/pokemon-species.json') as pokemon_species_file:
            species_data = json.load(pokemon_species_file)
            for species in species_data:
                self._species[species['name']] = species
                self._dex['national'][species['dex_national']] = species

        self._dex['hisui'] = {}
        with open(RESOURCE_PATH + '/resources/hisuidex.txt', 'r') as hisuidex_file:
            lines = hisuidex_file.readlines()
            for line in lines:
                [number, name] = line.strip().split('\t')
                species = self.species(name)
                if species != None:
                    species['dex_hisui'] = number
                    self._dex['hisui'][int(number)] = species
        

    def species(self, species_name: str):
        if species_name in self._species:
            return self._species[species_name]
        else:
            # Try and deal with forms
            parts = species_name.split('-')
            if len(parts) > 0 and parts[0] in self._species:
                return self._species[parts[0]]

        return None

    def species_by_dex(self, number: int, dex_name: str = 'national'):
        return self._dex[dex_name][number]

    def species_by_hisuidex(self, number: int):
        return self.species_by_dex(number, 'hisui')
    
    def dex(self, dex_name):
        return [self._dex[dex_name][key] for key in sorted(self._dex[dex_name])]
    
    def nationaldex(self):
        return self.dex('national')

    def hisuidex(self):
        return self.dex('hisui')
