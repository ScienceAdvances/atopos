import itertools
import re
import numpy as np
import pandas as pd
from ..st import removes,subs
from ._frame import select


# flatten a nest list
# flatten = lambda nest_list: sum(([x] if not isinstance(x, list) else flatten(x) for x in nest_list), [])

def dict_slice(adict:dict, start:int, end:int)->dict:
    '''
    slice a dict using numeric index
    '''
    keys = adict.keys()
    dict_slice = {}
    for k in list(keys)[start:end]:
        dict_slice[k] = adict[k]
    return dict_slice

def flatten(nest_list):
    nl = nest_list.copy()
    import itertools
    for x,y in enumerate(nl):
        if not isinstance(y, list):
            nl[x] = [y]
    return list(itertools.chain.from_iterable(nl))


def unique_exprs(frame, reductions=np.median):
    """
    基因去重复
    frame: row_index = genenames, columns = samples
    """
    frame['Ref'] = frame.apply(reductions, axis=1)
    frame.sort_values(by='Ref', ascending=False, inplace=True)
    frame.drop(columns='Ref', inplace=True)
    frame['Ref'] = frame.index
    frame.drop_duplicates(subset='Ref', inplace=True)
    return frame.drop(columns='Ref')

def get_TCGA_mRNA(arrow, dtype='tpm', label="01A", gene_type:list=None, barcode_length=16):
    _df = pd.read_feather(arrow)
    _df.loc[:,"gene_id"] = removes(string=_df.gene_id,pattern=r"\.\d+")
    _df.set_index(keys="gene_id", drop=True, inplace=True)

    # 筛选编码蛋白基因
    if gene_type:
        _df = _df.loc[_df.gene_type.isin(gene_type), :]
    # 筛选数据
    _df = select(frame=_df,columns=["gene_name","gene_type"], pattern=re.compile(pattern=f"^{dtype}_"))

    _df.columns = removes(
        string=_df.columns.values, pattern=re.compile(pattern=f"^{dtype}_"))

    _df = select(frame=_df,columns=["gene_name","gene_type"], pattern=re.compile(pattern=f"^.{{13}}{label}"))
    # barcode_length of samples
    _df.columns = subs(string=_df.columns.values, start=0, stop=barcode_length)

    return _df

