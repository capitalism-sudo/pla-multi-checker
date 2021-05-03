# Go to root of PyNXReader
import sys
sys.path.append('../')
from lookups import Util

print(Util.STRINGS.abilities[Util.PT.getFormeEntry(869,2).Ability1()])