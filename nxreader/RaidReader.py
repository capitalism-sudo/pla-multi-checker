from nxreader import SWSHReader
from structure import Den

class RaidReader(SWSHReader):
    def __init__(self,ip,port = 6000, usb_connection = False):
        if ip == None and not usb_connection:
            raise Exception("No IP Configured and usb_connection = False")
        SWSHReader.__init__(self,ip,port,usb_connection=usb_connection)
        from structure import EncounterNest8Archive, NestHoleDistributionEncounter8Archive
        buf = bytearray(open('../resources/bytes/local_raid','rb').read())
        Den.LOCALTABLE = EncounterNest8Archive.GetRootAsEncounterNest8Archive(buf,0)
        buf = self.readEventBlock_RaidEncounter('Event/Current/')
        Den.EVENTTABLE = NestHoleDistributionEncounter8Archive.GetRootAsNestHoleDistributionEncounter8Archive(buf,0x20)
        self.resets = 0

    def setTargetDen(self, denId):
        self.denID = denId - 1

    def getDenData(self):
        return Den(self.readDen(self.denID))
    
    def setWatts(self,watts):
        self.Watts = watts

    def readWatts(self):
        from structure import MyStatus8
        newWatts = MyStatus8(self.read(0x45068FE8, 0x3)).currentWatts()
        diffWatts = newWatts - self.Watts
        self.Watts = newWatts
        print(f"Watts: {newWatts} (+{diffWatts})")
