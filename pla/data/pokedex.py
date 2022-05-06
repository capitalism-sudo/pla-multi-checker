import json
from dataclasses import dataclass
from app import RESOURCE_PATH
from .gender import Gender


@dataclass(frozen=True)
class DexEntry():
    """Class for keeping track of a dex entry"""
    id: str
    index: int
    species: str
    form_id: str
    form_name: str
    gender_ratio: int    
    is_gender_dimorphic: bool = False

    def __post_init__(self):
        _dex_numbers: dict[str, int] = {}
        object.__setattr__(self, '_dex_numbers', _dex_numbers)

    def dex_number(self, dex_name: str = 'national'):
        return self._dex_numbers.get(dex_name)
    
    def set_dex_number(self, dex_name: str, number: int):
        self._dex_numbers[dex_name] = number

    def display_name(self):
        if self.form_name == '':
            return self.species
        else:
            return f"{self.species} ({self.form_name})"
    
    def calculate_gender(self, gender_value: int) -> Gender:
        if self.gender_ratio < 0 or self.gender_ratio >= 255:
            return Gender.GENDERLESS
        if self.gender_ratio == 0:
            return Gender.MALE
        if self.gender_ratio == 254:
            return Gender.FEMALE

        if gender_value < self.gender_ratio:
            return Gender.FEMALE
        else:
            return Gender.MALE
    
    def is_genderless(self):
        return self.gender_ratio < 0 or self.gender_ratio >= 255
    
    def is_fixed_gender(self):
        return self.gender_ratio <= 0 or self.gender_ratio >= 254
    
    def is_base_form(self):
        return self.form_id == '0'
    

class Pokedex():
    def __init__(self):
        # Three indexes
        self._entries: dict[str, DexEntry] = {}
        self._index: dict[int, DexEntry] = {}
        self._forms: dict[str, dict[str, DexEntry]] = {}
        self._dex: dict[str, dict[int, DexEntry]] = {}
        self._dex['national'] = {}

        with open(RESOURCE_PATH + 'resources/pokedex.json') as pokedex_file:
            species_data = json.load(pokedex_file)
            for entry_data in species_data:
                entry = DexEntry(entry_data['id'],
                                entry_data['index'],
                                entry_data['species'],
                                entry_data['form_id'],
                                entry_data['form_name'],
                                entry_data['gender_ratio'],
                                entry_data['gender_dimorphic'])
                self._entries[entry.id] = entry
                self._index[entry.index] = entry

                species  = self._forms.get(entry.species, {})
                species[entry.form_id] = entry
                self._forms[entry.species] = species

                self._dex['national'][entry_data['dex_national']] = entry
                entry.set_dex_number('national', entry_data['dex_national'])

        self._dex['hisui'] = {}
        with open(RESOURCE_PATH + 'resources/hisuidex.txt', 'r') as hisuidex_file:
            lines = hisuidex_file.readlines()
            for line in lines:
                [number, id] = line.strip().split('\t')
                number = int(number)
                entry = self._entries.get(id)

                if entry is not None:
                    self._dex['hisui'][number] = entry
                    species = self._forms[entry.species]
                    for pokemon in species.values():
                        pokemon.set_dex_number('hisui', number)

    def entry(self, id: str):
        return self._entries.get(id)

    def forms(self, species_name: str):
        return self._forms.get(species_name, {}).copy()

    def entry_by_dex(self, number: int, dex_name: str = 'national'):
        return self._dex[dex_name][number]

    def entry_by_index(self, index: int):
        return self._index[index]
    
    def dex(self, dex_name):
        return [self._dex[dex_name][key] for key in sorted(self._dex[dex_name])]
    
    def nationaldex(self):
        return self.dex('national')

    def hisuidex(self):
        return self.dex('hisui')