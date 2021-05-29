from structure.ByteStruct import ByteStruct
import math

class PK8(ByteStruct):
	STOREDSIZE = 0x148
	PARTYSIZE = 0x158
	BLOCKSIZE = 0x50
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

	def __init__(self,buf):
		self.data = bytearray(buf[:])
		if self.isEncrypted:
		 	self.decrypt()

	@property
	def ec(self):
		return self.getuint(0x0)

	@property
	def checksum(self):
		return self.getushort(0x6)

	@property
	def species(self):
		return self.getushort(0x8)

	@property
	def helditem(self):
		return self.getushort(0xA)

	@property
	def sidtid(self):
		return self.getuint(0x0C)

	@property
	def ability(self):
		return self.getushort(0x14)

	@property
	def abilityNum(self):
		return self.getbyte(0x16) & 0x7

	@property
	def getAbilityString(self):
		return self.abilityNum if self.abilityNum < 4 else 'H'

	@property
	def canGigantamax(self):
		return (self.getbyte(0x16) & 16) != 0

	@property
	def pid(self):
		return self.getuint(0x1C)

	@property
	def nature(self):
		return self.getbyte(0x20)

	@property
	def statnature(self):
		return self.getbyte(0x21)

	@property
	def gender(self):
		return (self.getbyte(0x22) >> 2) & 0x3

	@property
	def altForm(self):
		return self.getushort(0x24)

	@property
	def evs(self):
		return [self.data[0x26],self.data[0x27],self.data[0x28],self.data[0x2A],self.data[0x2B],self.data[0x29]]

	@property
	def move1(self):
		return self.getushort(0x72)

	@property
	def move2(self):
		return self.getushort(0x74)

	@property
	def move3(self):
		return self.getushort(0x76)

	@property
	def move4(self):
		return self.getushort(0x78)

	@property
	def iv32(self):
		return self.getuint(0x8C)

	@property
	def language(self):
		return self.getbyte(0xE2)

	@property
	def ball(self):
		return self.getbyte(0x124)

	@property
	def homeTracker(self):
		return self.getulong(0x135)

	@property
	def battleStats(self): # Lv,HP,Atk,Def,SpA,SpD,Spe
		return self.getbyte(0x148),self.getushort(0x14A),self.getushort(0x14C),self.getushort(0x14E),self.getushort(0x152),self.getushort(0x154),self.getushort(0x150)

	@property
	def isEgg(self):
		return ((self.iv32 >> 31) & 1) == 1

	@property
	def ivs(self):
		iv32 = self.iv32
		return [iv32 & 0x1F, (iv32 >> 5) & 0x1F, (iv32 >> 10) & 0x1F, (iv32 >> 20) & 0x1F, (iv32 >> 25) & 0x1F, (iv32 >> 15) & 0x1F]

	@property
	def mark(self):
		# probably bad approach to getting marks but it works for wilds
		if self.getbyte(0x3A) > 5:
			marks = ["Lunchtime","SleepyTime","Dusk"]
			return marks[int(math.log2(self.getbyte(0x3A)))-5]
		if self.getbyte(0x3B) > 0:
			marks = ["Dawn","Cloudy","Rainy","Stormy","Snowy","Blizzard","Dry","Sandstorm"]
			return marks[int(math.log2(self.getbyte(0x3B)))]
		if self.getbyte(0x40) > 0:
			marks = ["Misty","Destiny","Fishing","Curry","Uncommon","Rare","Rowdy","AbsentMinded"]
			return marks[int(math.log2(self.getbyte(0x40)))]
		if self.getbyte(0x41) > 0:
			marks = ["Jittery","Excited","Charismatic","Calmness","Intense","ZonedOut","Joyful","Angry"]
			return marks[int(math.log2(self.getbyte(0x41)))]
		if self.getbyte(0x42) > 0:
			marks = ["Smiley","Teary","Upbeat","Peeved","Intellectual","Ferocious","Crafty","Scowling"]
			return marks[int(math.log2(self.getbyte(0x42)))]
		if self.getbyte(0x43) > 0:
			marks = ["Kindly","Flustered","PumpedUp","ZeroEnergy","Prideful","Unsure","Humble","Thorny"]
			return marks[int(math.log2(self.getbyte(0x43)))]
		if self.getbyte(0x44) > 0:
			marks = ["Vigor","Slump"]
			return marks[int(math.log2(self.getbyte(0x44)))]
		
		return ""

	def calChecksum(self):
		chk = 0
		for i in range(8,PK8.STOREDSIZE,2):
			chk += self.getushort(i)
			chk &= 0xFFFF
		return chk

	@staticmethod
	def getShinyType(otid,pid):
		xor = (otid >> 16) ^ (otid & 0xFFFF) ^ (pid >> 16) ^ (pid & 0xFFFF)
		if xor > 15:
			return 0
		else:
			return 2 if xor == 0 else 1

	@property
	def shinyType(self):
		return self.getShinyType(self.sidtid,self.pid)

	@property
	def shinyString(self):
		return 'None' if self.shinyType == 0 else 'Star' if self.shinyType == 1 else 'Square'

	def save(self,filename):
		with open(f'{filename}.pk8','wb') as fileOut:
			fileOut.write(self.data)

	def __str__(self):
		from lookups import Util
		if self.isValid:
			shinytype = self.shinyType
			shinyflag = '' if shinytype == 0 else '⋆ ' if shinytype == 1 else '◇ '
			msg = f'EC: {self.ec:X}  PID: {self.pid:X}  ' + shinyflag
			msg += f"{'G-' if self.canGigantamax else ''}{Util.STRINGS.species[self.species]}{('-' + str(self.altForm)) if self.altForm > 0 else ''}\n"
			msg += f"Nature: {Util.STRINGS.natures[self.nature]}({Util.STRINGS.natures[self.statnature]})  "
			msg += f"Ability: {Util.STRINGS.abilities[self.ability]}({self.abilityNum if self.abilityNum < 4 else 'H'})  "
			msg += f"Gender: {Util.GenderSymbol[self.gender]}\n"
			msg += f"IVs: {self.ivs}  EVs: {self.evs}\n"
			msg += f"Moves: {Util.STRINGS.moves[self.move1]} / {Util.STRINGS.moves[self.move2]} / {Util.STRINGS.moves[self.move3]} / {Util.STRINGS.moves[self.move4]}\n"
			return msg
		else:
			return 'Invalid Data'

	@property
	def isValid(self):
	    return self.checksum == self.calChecksum() and not self.isEncrypted

	@property
	def isEncrypted(self):
		return self.getushort(0x70) != 0 and self.getushort(0xC0) != 0

	def decrypt(self):
		seed = self.ec
		sv = (seed >> 13) & 0x1F

		self.__cryptPKM__(seed)
		self.__shuffle__(sv)
	
	def __cryptPKM__(self,seed):
		self.__crypt__(seed, 8, PK8.STOREDSIZE)
		if len(self.data) == PK8.PARTYSIZE:
			self.__crypt__(seed, PK8.STOREDSIZE, PK8.PARTYSIZE)

	def __crypt__(self, seed, start, end):
		i = start
		while i < end:
			seed = seed * 0x41C64E6D + 0x00006073
			self.data[i] ^= (seed >> 16) & 0xFF
			i += 1
			self.data[i] ^= (seed >> 24) & 0xFF
			i += 1

	def __shuffle__(self, sv):
		idx = 4 * sv
		sdata = bytearray(self.data[:])
		for block in range(4):
			ofs = PK8.BLOCKPOSITION[idx + block]
			self.data[8 + PK8.BLOCKSIZE * block : 8 + PK8.BLOCKSIZE * (block + 1)] = sdata[8 + PK8.BLOCKSIZE * ofs : 8 + PK8.BLOCKSIZE * (ofs + 1)]

	def refreshChecksum(self):
		self.setushort(0x6, self.calChecksum())

	def encrypt(self):
		self.refreshChecksum()
		seed = self.ec
		sv = (seed >> 13) & 0x1F

		self.__shuffle__(PK8.blockPositionInvert[sv])
		self.__cryptPKM__(seed)
		return self.data

	blockPositionInvert = [
            0, 1, 2, 4, 3, 5, 6, 7, 12, 18, 13, 19, 8, 10, 14, 20, 16, 22, 9, 11, 15, 21, 17, 23,
            0, 1, 2, 4, 3, 5, 6, 7,
    ];

	BLOCKPOSITION = [
        0, 1, 2, 3,
        0, 1, 3, 2,
        0, 2, 1, 3,
        0, 3, 1, 2,
        0, 2, 3, 1,
        0, 3, 2, 1,
        1, 0, 2, 3,
        1, 0, 3, 2,
        2, 0, 1, 3,
        3, 0, 1, 2,
        2, 0, 3, 1,
        3, 0, 2, 1,
        1, 2, 0, 3,
        1, 3, 0, 2,
        2, 1, 0, 3,
        3, 1, 0, 2,
        2, 3, 0, 1,
        3, 2, 0, 1,
        1, 2, 3, 0,
        1, 3, 2, 0,
        2, 1, 3, 0,
        3, 1, 2, 0,
        2, 3, 1, 0,
        3, 2, 1, 0,

        # duplicates of 0-7 to eliminate modulus
        0, 1, 2, 3,
        0, 1, 3, 2,
        0, 2, 1, 3,
        0, 3, 1, 2,
        0, 2, 3, 1,
        0, 3, 2, 1,
        1, 0, 2, 3,
        1, 0, 3, 2,
    ];
