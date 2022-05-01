from pla.data import SPECIES, RATIOS, GENDERLESS

# This might not be the best place for these functions, but collecting them here for now

def get_gender_string(species, gender):
    if species in GENDERLESS:
        return "Genderless <i class='fa-solid fa-genderless'/>"

    ratio = RATIOS[str(SPECIES.index(species))][2]
    if gender <= ratio:
       return "Female <i class='fa-solid fa-venus' style='color:pink'/>"
    else:
        return "Male <i class='fa-solid fa-mars' style='color:blue'/>"

def get_sprite(species, form, shiny):
    return f"c_{SPECIES.index(species)}{'-' + form if len(form) != 0 else ''}{'s' if shiny else ''}.png"

def get_path_display(index, value, epath):
    string = "["
    for p,val in enumerate(value):
        if p != 0:
            string = string + f", D{val}"
        else:
            string = string + f"D{val}"
    string = string + "]"
    
    if epath == []:
        return f"<span class='pla-results-firstpath'>" \
                    f"First Round Path: " \
                    f"{string} </span> + [Clear Round] + " \
                    f"<span class='pla-results-bonus'> Bonus " \
                    + index
    else:
        return f"<span class='pla-results-firstpath'>First Round Path: " \
                    f"{string} </span> + <span class='pla-results-revisit'> " \
                    f"Revisit {epath} </span> + <span class='pla-results-bonus'> " \
                    f"Bonus " \
                    + index

def get_rolls(research, species, base_level):
    rolls = base_level
    if research['shinycharm']:
        rolls += 3
    
    if species in research['rolls']:
        rolls += research['rolls'][species]
    else:
        print(f"No research found for {species}")
    
    return rolls