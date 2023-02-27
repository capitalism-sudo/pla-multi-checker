RESOURCE_PATH = './static/'

with open(RESOURCE_PATH + "resources/text_natures.txt",encoding="utf-8") as text_natures:
    _natures = text_natures.read().split("\n")

type = [
    "Fighting",
    "Flying",
    "Poison",
    "Ground",
    "Rock",
    "Bug",
    "Ghost",
    "Steel",
    "Fire",
    "Water",
    "Grass",
    "Electric",
    "Psychic",
    "Ice",
    "Dragon",
    "Dark"
]

def natures(nature_id):
    return _natures[nature_id]

def pktype(hidden):
    return type[hidden]

def calcSlot(compare, ranges, rod=0):
    for i in range(rod,len(ranges)+rod):
        if compare < ranges[i-rod]:
            return i
    return 255

def getSlotRanges(result, enctype):
    compare = result % 100

    if enctype == "OldRod":
        return calcSlot(compare, [70,100],0)
    elif enctype == "GoodRod":
        return calcSlot(compare, [60,80,100],2)
    elif enctype == "SuperRod":
        return calcSlot(compare, [40,80,95,99,100],5)
    elif enctype == "Surfing" or enctype == "RockSmash":
        return calcSlot(compare, [60,90,95,99,100])
    else:
        return calcSlot(compare, [20,40,50,60,70,80,85,90,94,98,99,100])
    
def calcCharm(ratio,pid):
    if ratio == "31f":
        return (pid & 0xff) < 31
    elif ratio == "31m":
        return (pid & 0xff) >= 31
    elif ratio == "63f":
        return (pid & 0xff) < 63
    elif ratio == "63m":
        return (pid & 0xff) >= 63
    elif ratio == "127f":
        return (pid & 0xff) < 127
    elif ratio == "127m":
        return (pid & 0xff) >= 127
    elif ratio == "191f":
        return (pid & 0xff) < 191
    elif ratio == "191m":
        return (pid & 0xff) >= 191
    else:
        return True
    
def setLevel(slot,compare,encounter):
    species = encounter['mons'][slot]['species'].replace("SPECIES_",'').title()
    return (compare % (encounter['mons'][slot]['max_level'] - encounter['mons'][slot]['min_level'] + 1) + encounter['mons'][slot]['min_level']), species

def get_bdsp_sprite(species, shiny: bool = False):
    form_flag = ''
    gender_flag = ''
    shiny_flag = 's' if shiny else ''
    return f"c_{species}{form_flag}{gender_flag}{shiny_flag}.png"