from structure.ByteStruct import ByteStruct

class MyStatus7b(ByteStruct):

	def TID(self):
		return self.getushort(0x0)

	def SID(self):
		return self.getushort(0x2)

	def TSV(self):
		return (self.TID() ^ self.SID()) >> 4

	def displayID(self):
		return self.getuint(0x0) % 1000000

	def Game(self):
		return self.getbyte(0x4)

	def Language(self):
		return self.getbyte(0x35)

	def getLangName(self):
		langNames = {1:'Japanese', 2:'English', 3:'French', 4:'Italian', 5:'German', 7:'Spanish', 8:'Korean', 9:'Simpl. Chinese', 10:'Tradit. Chinese'}
		return langNames[self.Language()]

	def OT(self):
		return self.getstring(0x38,0x1A)
