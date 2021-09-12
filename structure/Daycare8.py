# Class to read the daycare
# (https://github.com/kwsch/PKHeX/blob/master/PKHeX.Core/Saves/Substructures/Gen8/Daycare8.cs)

from rng.G8RNG import Egg
from structure.ByteStruct import ByteStruct
from structure.PK8 import PK8

class Daycare8(ByteStruct):
    ROUTE_5 = 0
    WILD_AREA = 1
    # 0x2 + 0x4 + 0x8 + 0x18
    META_SIZE = 0x26
    # present bool + pk8
    STRUCT_SIZE = 1 + 0x148
    # two pokemon + meta
    DAYCARE_SIZE = (2 * STRUCT_SIZE) + META_SIZE

    def __init__(self,reader):
        self.reader = reader
        self.data = bytearray(reader.readDaycare()[:])
        self.tid, self.sid = reader.TrainerSave.TID(), reader.TrainerSave.SID()
        self.internal_egg = None
    
    def refresh(self):
        try:
            self.data = bytearray(self.reader.readDaycare()[:])
        except:
            pass
        
    def present(self,daycare,slot):
        return self.data[self.DAYCARE_SIZE*daycare + self.STRUCT_SIZE * (slot-1)]
    
    def parent(self,daycare,slot):
        return self.data[self.DAYCARE_SIZE*daycare + self.STRUCT_SIZE * (slot-1) + 1:self.DAYCARE_SIZE*daycare + self.STRUCT_SIZE * (slot-1) + 1 + 0x148]
    
    def seed(self,daycare):
        return self.getulong(self.DAYCARE_SIZE*daycare + self.STRUCT_SIZE * 2 + 6)
    
    def steps(self,daycare):
        return self.getuint(self.DAYCARE_SIZE*daycare + self.STRUCT_SIZE * 2 + 2)
    
    def egg(self,daycare,shinycharm):
        parent1, parent2 = PK8(self.parent(daycare,1)),PK8(self.parent(daycare,2))
        if self.internal_egg == None or self.internal_egg.parents != [parent1.ec,parent2.ec] or shinycharm != self.internal_egg.ShinyCharm:
            self.internal_egg = Egg(self.seed(daycare),parent1,parent2,shinycharm,self.tid,self.sid)
        elif self.internal_egg.seed != self.seed(daycare):
            self.internal_egg.reseed(self.seed(daycare))
        return self.internal_egg