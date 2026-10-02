from ..st import detects
import pandas as pd
from typing import Union, Optional


def select(frame, columns=None, pattern=None):
    """
    select a DataFrame columns according to `subsets` conditions
    """
    _objs = []
    if columns:
        cidx = frame.columns.isin(values=columns)
        _objs.append(frame.loc[:, cidx])
    if pattern:
        cidx = detects(string=frame.columns, pattern=pattern)
        _objs.append(frame.loc[:, cidx])
    return pd.concat(objs=_objs,axis=1)


def subset(
    frame: pd.DataFrame,
    subsets: dict,
    inplace: bool = False
) -> Optional[pd.DataFrame]:
    """
    filter/subset a DataFrame according to `subsets` conditions
    """
    _f = frame if inplace else frame.copy()
    for k in subsets:
        v = subsets.get(k)
        if isinstance(v, list):
            _lg = _f[k].isin(v)
            _f = _f.loc[_lg, :]
        else:
            _lg = _f[k].apply(lambda x: eval(v))
            _f = _f.loc[_lg, :]
    return None if inplace else _f
