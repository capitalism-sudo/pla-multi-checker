from structure.ByteStruct import ByteStruct

class PK7b(ByteStruct):
	STOREDSIZE = 260
	PARTYSIZE = 260
	BLOCKSIZE = 56

	def __init__(self,buf):
		self.data = bytearray(buf[:])
		if self.isEncrypted():
		 	self.decrypt()

	def ec(self):
		return self.getuint(0x0)

	def checksum(self):
		return self.getushort(0x6)

	def species(self):
		return self.getushort(0x8)

	def helditem(self):
		return self.getushort(0xA)

	def sidtid(self):
		return self.getuint(0x0C)

	def ability(self):
		return self.getbyte(0x14)

	def abilityNum(self):
		return self.getbyte(0x15) & 0x7

	def getAbilityString(self):
		return self.abilityNum() if self.abilityNum() < 4 else 'H'

	def pid(self):
		return self.getuint(0x18)

	def nature(self):
		return self.getbyte(0x1C)

	def gender(self):
		return (self.getbyte(0x1D) >> 1) & 0x3

	def evs(self):
		return [self.data[0x1E],self.data[0x1F],self.data[0x20],self.data[0x21],self.data[0x22],self.data[0x23]]

	def move1(self):
		return self.getushort(0x5A)

	def move2(self):
		return self.getushort(0x5C)

	def move3(self):
		return self.getushort(0x5E)

	def move4(self):
		return self.getushort(0x60)

	def iv32(self):
		return self.getuint(0x74)

	def ivs(self):
		iv32 = self.iv32()
		return [iv32 & 0x1F, (iv32 >> 5) & 0x1F, (iv32 >> 10) & 0x1F, (iv32 >> 20) & 0x1F, (iv32 >> 25) & 0x1F, (iv32 >> 15) & 0x1F]

	@staticmethod
	def getShinyType(otid,pid):
		xor = (otid >> 16) ^ (otid & 0xFFFF) ^ (pid >> 16) ^ (pid & 0xFFFF)
		if xor > 15:
			return 0
		else:
			return 2 if xor == 0 else 1

	def shinyType(self):
		return self.getShinyType(self.sidtid(),self.pid())

	def shinyString(self):
		return 'None' if self.shinyType() == 0 else 'Star' if self.shinyType() == 1 else 'Square'

	def save(self,filename):
		with open(f'{filename}.PK7b','wb') as fileOut:
			fileOut.write(self.data)

	def toString(self):
		from lookups import Util
		if self.isValid():
			shinytype = self.shinyType()
			shinyflag = '' if shinytype == 0 else '⋆ ' if shinytype == 1 else '◇ '
			msg = f'EC: {self.ec():X}  PID: {self.pid():X}  ' + shinyflag
			msg += f"{Util.STRINGS.species[self.species()]}\n"
			msg += f"Nature: {Util.STRINGS.natures[self.nature()]}  "
			msg += f"Ability: {Util.STRINGS.abilities[self.ability()]}({self.abilityNum() if self.abilityNum() < 4 else 'H'})  "
			msg += f"Gender: {Util.GenderSymbol[self.gender()]}\n"
			msg += f"IVs: {self.ivs()}  EVs: {self.evs()}\n"
			msg += f"Moves: {Util.STRINGS.moves[self.move1()]} / {Util.STRINGS.moves[self.move2()]} / {Util.STRINGS.moves[self.move3()]} / {Util.STRINGS.moves[self.move4()]}\n"
			return msg
		else:
			return 'Invalid Data'

	def isValid(self):
	    return not self.isEncrypted()

	def isEncrypted(self):
		return self.getushort(0xC8) != 0 or self.getushort(0x58) != 0

	def decrypt(self):
		seed = self.ec()
		sv = (seed >> 13) & 0x1F

		self.__cryptPKM__(seed)
		self.__shuffle__(sv)
	
	def __cryptPKM__(self,seed):
		self.__crypt__(seed, 8, PK7b.STOREDSIZE)
		if len(self.data) == PK7b.PARTYSIZE:
			self.__crypt__(seed, PK7b.STOREDSIZE, PK7b.PARTYSIZE)

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
			ofs = PK7b.BLOCKPOSITION[idx + block]
			self.data[8 + PK7b.BLOCKSIZE * block : 8 + PK7b.BLOCKSIZE * (block + 1)] = sdata[8 + PK7b.BLOCKSIZE * ofs : 8 + PK7b.BLOCKSIZE * (ofs + 1)]

	def refreshChecksum(self):
		self.setushort(0x6, self.calChecksum())

	def encrypt(self):
		self.refreshChecksum()
		seed = self.ec()
		sv = (seed >> 13) & 0x1F

		self.__shuffle__(PK7b.blockPositionInvert[sv])
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
