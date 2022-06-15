# Filters

def no_filter(pokemon):
    return True
    
def is_shiny(pokemon):
    return pokemon['shiny'] == True

def is_square(pokemon):
    return pokemon['square'] == True

def is_square_shiny(pokemon):
    return pokemon['square'] == True

def is_rare(pokemon):
    return pokemon['rarespawn']

def is_perfect(pokemon):
    return pokemon['ivs'] == [31, 31, 31, 31, 31, 31]

def is_perfect_physical(pokemon):
    ivs = pokemon['ivs']
    return ivs[0] == 31 and ivs[1] == 31 and ivs[2] == 31 and ivs[4] == 31 and ivs[5] == 31 

def is_perfect_special(pokemon):
    ivs = pokemon['ivs']
    return ivs[0] == 31 and ivs[2] == 31 and ivs[3] == 31 and ivs[4] == 31 and ivs[5] == 31

def no_attack(pokemon):
    return pokemon['ivs'][1] == 0

def no_speed(pokemon):
    return pokemon['ivs'][5] == 0

def num_perfect_ivs(pokemon):
    return sum(1 for iv in pokemon['ivs'] if iv == 31)

def num_30plus_ivs(pokemon):
    return sum(1 for iv in pokemon['ivs'] if iv >= 30)
    
def has_3ivs(pokemon):
    return num_perfect_ivs(pokemon) >= 3
    
def has_4ivs(pokemon):
    return num_perfect_ivs(pokemon) >= 4
    
def has_5ivs(pokemon):
    return num_perfect_ivs(pokemon) >= 5

def has_1ivs(pokemon):
    return num_perfect_ivs(pokemon) >= 1

def has_2ivs(pokemon):
    return num_perfect_ivs(pokemon) >= 2

def is_shiny_6iv(pokemon):
    return is_shiny(pokemon) and is_perfect(pokemon)

def is_shiny_alpha(pokemon):
    return is_shiny(pokemon) and is_alpha(pokemon)

def has_no_attack_5iv(pokemon):
    return no_attack(pokemon) and has_5ivs(pokemon)

def has_6iv_over_30(pokemon):
    return num_30plus_ivs(pokemon) == 6

def has_5iv_over_30(pokemon):
    return num_30plus_ivs(pokemon) >= 5

def has_2iv_over_30(pokemon):
    return num_30plus_ivs(pokemon) >= 2

def has_3iv_over_30(pokemon):
    return num_30plus_ivs(pokemon) >= 3 

def has_4iv_over_30(pokemon):
    return num_30plus_ivs(pokemon) >= 4   

def has_no_attack_5iv_over_30(pokemon):
    return no_attack(pokemon) and (num_30plus_ivs(pokemon) == 5)

def has_no_speed_5iv_over_30(pokemon):
    return no_speed(pokemon) and (num_30plus_ivs(pokemon) == 5)

def has_no_speed_5iv(pokemon):
    return no_speed(pokemon) and has_5ivs(pokemon)

def has_no_speed_no_attack(pokemon):
    return no_speed(pokemon) and no_attack(pokemon)

def has_no_speed_no_attack_4iv_over_30(pokemon):
    return no_speed(pokemon) and no_attack(pokemon) and (num_30plus_ivs(pokemon) == 4)

def has_no_speed_no_attack_4iv(pokemon):
    return no_speed(pokemon) and no_attack(pokemon) and has_4ivs(pokemon)


#IV Filters

def compare_single_iv(miniv, maxiv, iv):
    return miniv <= iv <= maxiv

def compare_all_ivs(minivs, maxivs, ivs):
    for i in range(6):
        
        if not compare_single_iv(int(minivs[i]), int(maxivs[i]), int(ivs[i])):
            return False
    
    return True