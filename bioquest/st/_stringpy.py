import numpy as np
import re

def sub(string,start=0,stop=-1) -> str:
    return string[start:stop]

def detect(pattern: str, string: str, flags=0) -> bool:
    return False if re.search(pattern=pattern,string=string,flags=flags) is None else True

def replace(pattern: str, repl: str, string: str, count:int = 0):
    return re.sub(pattern=pattern,repl=repl,string=string, count=count)

def grep(pattern: str, string: str, flags=0):
    bl = detect(pattern=pattern,string=string,flags=flags)
    return list(np.array(string)[bl])

def count(pattern: str, string: str, flags=0):
    return len(re.findall(pattern=pattern,string=string,flags=flags))