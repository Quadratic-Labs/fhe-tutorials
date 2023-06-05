from concrete import fhe
import numpy as np
from functools import reduce

def min_int(x: int, y: int) -> int:
    """concrete-numpy doesn't yet support min, we have to implement one using
    only supported operations"""
    return (x + y - abs(x - y)) // 2

def min_int_array(a) -> int:
    """Return the minimum value of an array of ints using the `min_int` function"""
    return reduce(min_int, a)

def knn(distances):
    """Return the index of the K minimum values (nearest neighbors) from the distances array
    
    The output is an array with zeros but ones at the indexes of the K min values
    Note that the function could return more that K element if there are equal values
    """
    # if k is a parameter, we get: TypeError: 'Tracer' object cannot be interpreted as an integer
    k = 2
    inf = 9
    N, = distances.shape
    result = [0] * N

    for _ in range(k):
        # Get the minimum value of the array
        minimum = min_int_array(distances)
        # Get a selector for the value
        minimum_selector = distances == minimum
        # Add the selected index to the result array
        result = result | minimum_selector
        # Get a selector for the remaining element
        remaining_selector = (np.logical_not(minimum_selector.astype(bool))).astype(int)
        # set the selected value to inf
        distances = distances * remaining_selector + minimum_selector*inf
    
    return result