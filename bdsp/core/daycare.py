from pla.data import natures

class Daycare:

    def __init__(self, 
                oval_charm: bool, 
                shiny_charm: bool, 
                tid, 
                sid, 
                compatibility, 
                a_ivs, 
                b_ivs, 
                a_item, 
                b_item,
                masuda: bool,
                nido_volbeat: bool,
                a_nature,
                b_nature,
                a_ability,
                b_ability,
                a_ditto: bool,
                b_ditto: bool,
                gender_ratio):

        self.oval = oval_charm
        self.shiny = shiny_charm
        self.tid = tid
        self.sid = sid
        self.compatibility = compatibility
        self.a_iv = a_ivs
        self.b_iv = b_ivs
        self.a_item = a_item
        self.b_item = b_item
        self.masuda = masuda
        self.nido = nido_volbeat
        self.a_nature = a_nature
        self.b_nature = b_nature
        self.a_ability = a_ability
        self.b_ability = b_ability
        self.a_ditto = a_ditto
        self.b_ditto = b_ditto
        self.gender = gender_ratio

    def is_ditto(self, parent):
        if parent == 0:
            return self.a_ditto
        else:
            return self.b_ditto

    def has_oval_charm(self):
        return self.oval

    def get_compatibility(self):
        
        if self.has_oval_charm():
            if self.compatibility == 20:
                res = 40
            elif self.compatibility == 50:
                res = 80
            else:
                res = 88
            
            return res
        else:
            return self.compatibility
    
    def has_shiny_charm(self):
        return self.shiny

    def is_masuda(self):
        return self.masuda

    def get_pidrolls(self):
        pidrolls = 0

        if self.has_shiny_charm():
            pidrolls += 2
        if self.is_masuda():
            pidrolls += 6

        return pidrolls
    
    def is_nido_volbeat(self):
        return self.nido

    def get_everstone_count(self):
        res = 0
        res += 1 if self.a_item == 1 else 0
        res += 1 if self.b_item == 1 else 0

        return res

    def get_parent_item(self, parent: int):
        if parent == 0:
            return self.a_item
        else:
            return self.b_item

    def get_parent_nature(self, parent):
        if parent == 0:
            return self.a_nature
        else:
            return self.b_nature

    def get_parent_ability(self, parent):
        if parent == 0:
            return self.a_ability
        else:
            return self.b_ability

    def get_inherit(self):

        inherit = 3

        if self.get_parent_item(0) == 8 or self.get_parent_item(1) == 8:
            inherit = 5
        
        return inherit
    
    def get_parent_iv(self, index, parent):
        if parent == 0:
            return self.a_iv[index]
        else:
            return self.b_iv[index]

    def get_tid(self):
        return self.tid
    
    def get_sid(self):
        return self.sid

    def get_gender_ratio(self):
        return self.gender
