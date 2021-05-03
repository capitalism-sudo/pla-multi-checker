# Class to store info on overworld mons in their readable forms

class PK8():
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
    
    def __init__(self):
        self.species = 0
        self.form = 0
        self.currentlevel = 0
        self.met_level = 0
        self.gender = 0
        self.ot_name = ""
        self.tid = 0
        self.sid = 0
        self.nature = 0
        self.ability = 0
        self.PID = 0
        self.EC = 0
        self.ivs = [32]*6
        self.mark = -1

    def toString(self):
        from lookups import Util
        shinytype = self.getShinyType((self.sid<<16) | self.tid, self.PID)
        shinyflag = '' if shinytype == 0 else '⋆ ' if shinytype == 1 else '◇ '
        msg = f'EC: {self.EC:X}  PID: {self.PID:X}  ' + shinyflag
        msg += f"{Util.STRINGS.species[self.species]}{('-' + str(self.form)) if self.form > 0 else ''}\n"
        msg += f"Level {self.currentlevel}\n"
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

	