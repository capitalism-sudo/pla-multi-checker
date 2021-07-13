# Class to read Overworld Mons - can probably be improved
# (credit to https://github.com/Manu098vm/Sys-EncounterBot.NET/)

from structure.ByteStruct import ByteStruct
from structure.PK8Overworld import PK8

class KCoordinates(ByteStruct):
    
    def __init__(self,reader):
        self.reader = reader
        self.data = bytearray(reader.readKCoordinatesBlock()[:])
        self.tid, self.sid = reader.TrainerSave.TID(), reader.TrainerSave.SID()
    
    def refresh(self):
        self.data = bytearray(self.reader.readKCoordinatesBlock()[:])
        
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
            data = self.reader.read(offset, 56)
            species = int.from_bytes(data[2],"little")
            offset += 192
            i += 1
            while (target != 0 and species != 0 and target != species and i < 20):
                data = self.reader.read(offset, 56)
                species = int.from_bytes(data[:2],"little")
                offset += 192
                i += 1
        elif mondata != None:
            data = mondata
            species = int.from_bytes(data[:2],"little")
        
        if data != None and data[20] == 1:
            pkm = PK8(data,self.tid,self.sid)
            return pkm