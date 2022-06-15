import json
from ..filters import *

def flatten_ug(results, filter_result = True, filter_function = is_shiny):
    res = []
    #print("Printing Results for flatten_ug")
    #print(results)
   # print()
    #print()
    print(f"filter_result: {filter_result}")
    print(f"filter_function: {filter_function}")

    for value in results.values():
        res.extend(flatten_ug_advance(value, filter_result, filter_function))

    return res

def flatten_ug_advance(results, filter_result, filter_function):

    res = []
    #print("Printing result for flatten_ug_advance:")
    #print(results)
    #print()

    for _,value in enumerate(results):
        res.extend(flatten_ug_pokemon(value, filter_result, filter_function))
    
    return res

def flatten_ug_pokemon(results, filter_result, filter_function):

    if filter_result and filter_function(results):
        return [results]
    elif not filter_result:
        return [results]
    else:
        return []

def flatten_bdsp_stationary(results, filter_results, filter_function=is_shiny):

    res = []

    for value in results.values():
        res.extend(flatten_bdsp_stationary_advance(value, filter_results, filter_function))
    
    return res

def flatten_bdsp_stationary_advance(results, filter_results, filter_function):

    if filter_results and filter_function(results):
        return [results]
    elif not filter_results:
        return [results]
    else:
        return []