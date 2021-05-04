from structure.ByteStruct import ByteStruct
from structure.PK8Overworld import PK8
from rng import OverworldRNG
# Class to read Overworld Mons - can probably be improved
# (credit to https://github.com/Manu098vm/Sys-EncounterBot.NET/)

class KCoordinates(ByteStruct):
    
    def ReadOwPokemonFromBlock(self):
        PK8s = []
        i = 8
        j = 0
        last_index = 8
        count = 0
        while i < len(self.data):
            if j == 12:
                if self.data[i - 68] != 0 and self.data[i - 68] != 255:
                    bbytes = self.data[i-68:i-68+56]
                    j = 0
                    i = last_index + 8
                    last_index = i
                    count += 1
                    pkm = self.ReadOwPokemon(0, 0, bbytes)
                    if pkm != None:
                        PK8s.append(pkm)
            if self.data[i] == 255:
                if i % 8 == 0:
                    last_index = i
                i += 1
                j += 1
            else:
                j = 0
                if i == last_index:
                    i += 8
                    last_index = i
                else:
                    i = last_index + 8
                    last_index = i
        return PK8s

    def ReadOwPokemon(self, target, startoffset, mondata):
        data = None
        species = 0
        offset = startoffset
        i = 0
        
        if target != 0:
            data = self.r.read(offset, 56)
            species = int.from_bytes(data[2],"little")
            offset += 192
            i += 1
            while (target != 0 and species != 0 and target != species and i < 20):
                data = self.r.read(offset, 56)
                species = int.from_bytes(data[:2],"little")
                offset += 192
                i += 1
        elif mondata != None:
            data = mondata
            species = int.from_bytes(data[:2],"little")
        
        if data != None and data[20] == 1:
            pkm = PK8()
            pkm.species = species
            pkm.form = data[2]
            pkm.currentlevel = data[4]
            pkm.metlevel = data[4]
            pkm.gender = 0 if data[10] == 1 else 1
            pkm.nature = data[8]
            pkm.ability = data[12] - 1
            pkm.mark = data[22]
            shinyness = data[6] + 1
            ivs = data[18]
            seed = int.from_bytes(data[24:28],"little") & 0xFFFFFFFF

            pkm = OverworldRNG.CalculateFromSeed(pkm, shinyness, ivs, seed)
            return pkm