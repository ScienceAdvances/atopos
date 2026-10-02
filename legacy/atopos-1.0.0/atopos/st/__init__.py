import functools
import numpy as np
from ._stringpy import *

# string
subs = np.vectorize(sub,otypes=[str])
replaces = np.vectorize(replace,otypes=[str])
detects = np.vectorize(detect,otypes=[bool])
remove = functools.partial(replace,repl='')
removes = np.vectorize(remove,otypes=[str])
counts = np.vectorize(count,otypes=[int])

def greps(pattern: str, string: str, flags=0):
    bl = detects(pattern=pattern,string=string,flags=flags)
    return list(np.array(string)[bl])