# Class to store info on overworld mons in their readable forms

from structure.ByteStruct import ByteStruct
from rng import OverworldRNG

class PK8(ByteStruct):
    Ribbons = """ChampionKalos,
        ChampionG3,
        ChampionSinnoh,
        BestFriends,
        Training,
        BattlerSkillful,
        BattlerExpert,
        Effort,
        Alert,
        Shock,
        Downcast,
        Careless,
        Relax,
        Snooze,
        Smile,
        Gorgeous,
        Royal,
        GorgeousRoyal,
        Artist,
        Footprint,
        Record,
        Legend,
        Country,
        National,
        Earth,
        World,
        Classic,
        Premier,
        Event,
        Birthday,
        Special,
        Souvenir,
        Wishing,
        ChampionBattle,
        ChampionRegional,
        ChampionNational,
        ChampionWorld,
        CountMemoryContest,
        CountMemoryBattle,
        ChampionG6Hoenn,
        ContestStar,
        MasterCoolness,
        MasterBeauty,
        MasterCuteness,
        MasterCleverness,
        MasterToughness,
        ChampionAlola,
        BattleRoyale,
        BattleTreeGreat,
        BattleTreeMaster,
        ChampionGalar,
        TowerMaster,
        MasterRank,
        Lunchtime,
        Sleepy-Time,
        Dusk,
        Dawn,
        Cloudy,
        Rainy,
        Stormy,
        Snowy,
        Blizzard,
        Dry,
        Sandstorm,
        Misty,
        Destiny,
        Fishing,
        Curry,
        Uncommon,
        Rare,
        Rowdy,
        Absent-Minded,
        Jittery,
        Excited,
        Charismatic,
        Calmness,
        Intense,
        Zoned-Out,
        Joyful,
        Angry,
        Smiley,
        Teary,
        Upbeat,
        Peeved,
        Intellectual,
        Ferocious,
        Crafty,
        Scowling,
        Kindly,
        Flustered,
        Pumped-Up,
        ZeroEnergy,
        Prideful,
        Unsure,
        Humble,
        Thorny,
        Vigor,
        Slump""".split(""",
        """)
    
    def __init__(self, data, tid, sid):
        self.data = data
        self.tid, self.sid = tid, sid
        self.calculateFromSeed()
    
    def calculateFromSeed(self):
        self.ec, self.pid, self.ivs = OverworldRNG.calculateFromSeed(self)

    @property
    def species(self):
        return self.getushort(0)
    
    @property
    def form(self):
        return self.data[2]
    
    @property
    def level(self):
        return self.data[4]
    
    @property
    def gender(self):
        if self.data[10] == 1:
            return 0
        elif self.data[10] == 0:
            return 1
        else:
            return 2
    
    @property
    def nature(self):
        return self.data[8]
    
    @property
    def ability(self):
        return self.data[12] - 1

    @property
    def mark(self):
        return self.data[22]
    
    @property
    def brilliant(self):
        return self.data[32]
    
    @property
    def setIVs(self):
        return self.data[18]
    
    @property
    def setShininess(self):
        return self.data[6] + 1
    
    @property
    def seed(self):
        return self.getuint(24)

    def __str__(self):
        from lookups import Util
        shinytype = self.getShinyType((self.sid<<16) | self.tid, self.pid)
        shinyflag = '' if shinytype == 0 else '⋆ ' if shinytype == 1 else '◇ '
        msg = f'EC: {self.ec:X}  PID: {self.pid:X}  ' + shinyflag
        msg += f"{Util.STRINGS.species[self.species]}{('-' + str(self.form)) if self.form > 0 else ''}\n"
        msg += f"Level {self.level}\n"
        msg += f"Nature: {Util.STRINGS.natures[self.nature]}  "
        msg += f"Ability: {self.ability if self.ability < 4 else 'H'}  "
        msg += f"Gender: {Util.GenderSymbol[self.gender]}\n"
        msg += f"IVs: {self.ivs}\n"
        msg += f"Mark: {self.Ribbons[self.mark] if self.mark != 255 else ''}\n"
        return msg
        
    @staticmethod
    def getShinyType(otid,pid):
        xor = (otid >> 16) ^ (otid & 0xFFFF) ^ (pid >> 16) ^ (pid & 0xFFFF)
        if xor > 15:
            return 0
        else:
            return 2 if xor == 0 else 1

	