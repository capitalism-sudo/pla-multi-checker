import json
from bdsp.filters import *

def flatten_ug(results, filter_result = True, filter_function = is_shiny):
    res = []
    print("Printing Results for flatten_ug")
    print(results)
    print()
    print()

    for value in results.values():
        res.extend(flatten_ug_advance(value, filter_result, filter_function))

    return res

def flatten_ug_advance(results, filter_result, filter_function):

    res = []
    print("Printing result for flatten_ug_advance:")
    print(results)
    print()

    for _,value in enumerate(results):
        res.extend(flatten_ug_pokemon(value, filter_result, filter_function))
    
    return res

def flatten_ug_pokemon(results, filter_result, filter_function):

    if filter_result and filter_function(results):
        return [results]
    else:
        return [results]
