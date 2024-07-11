import numpy as np
import pandas as pd
from ._frame import subset,select
from ._IO import read_csv_gz
import bioquest as bq
import re
import functools

def current_symbol(frame,reference,tax_id=9606):
    '''
    map SYMBOL alias to latest official SYMBOL NAME
    frame: dataframe,index is SYMBOL
    reference: dataframe, can download from ...
    '''
    alias=pd.read_feather(reference)
    alias = subset(alias,{"tax_id":[tax_id]})
    alias = select(alias,columns=["Symbol","Alias"])
    alias.set_index(keys="Symbol",drop=True,inplace=True)
    lg = frame.index.isin(alias.index)
    new = pd.merge(frame.loc[~lg,:],alias,left_index=True,right_on="Alias",how='left')
    
    return pd.concat([new,frame.loc[lg,:]])

def deg_siglabel(
        table: pd.DataFrame, 
        lfc='LFC',
        pvalue:str = "Pvalue", # "Padj"
        lfc_thr = (.585, .585),
        pv_thr =(.05, .05),
        siglabel=('Down', 'NS', 'Up'),
        inplace=True
        ) -> pd.DataFrame:
    """
    label genes for significant up/down or not significant
    lfc
    pvalue
    """
    # upregulated
    _table = table if inplace else table.copy()
    lg_up = np.logical_and(_table[lfc] >= lfc_thr[1],_table[pvalue] < pv_thr[1])
    _table.loc[lg_up,'Change'] = siglabel[2]
    # downregulated
    lg_down = np.logical_and(_table[lfc] <= -lfc_thr[0],_table[pvalue] < pv_thr[0])
    _table.loc[lg_down, 'Change'] = siglabel[0]
    _table.fillna(value={'Change': siglabel[1]}, inplace=True)
    # return _table
    print(f'All degs: {_table.loc[_table.Change != siglabel[1], :].shape[0]}')
    print(
        f'Up: {_table.loc[_table.Change == siglabel[2],:].shape[0]}')
    print(
        f'Down: {_table.loc[_table.Change == siglabel[0],:].shape[0]}')
    return None if inplace else _table

def deg_filter(
        frame: pd.DataFrame,
        lfc :str='LFC',
        top_n=None,
        filter_label=['Up','Down']
        ) -> pd.DataFrame:
    if top_n:
        _df = frame.sort_values(by=lfc)
        nrow = frame.shape[0]
        dfslice = list(range(0, top_n)) + \
            list(range(nrow-top_n, nrow))
        return _df.iloc[dfslice, :]
    else:
        return subset(frame,{"Change":filter_label})

def deseq(
        fdata: pd.DataFrame,
        pdata: pd.DataFrame,
        case: str,
        ref: str,
        n_jobs: int = 2) -> pd.DataFrame:
    """
    differential expression analysis (DEA) with bulk RNA-seq data
    fdata:pandas.DataFrame One column per gene, rows are indexed by sample barcodes.
    pdata:pandas.DataFrame, first column is Group
    """
    import pydeseq2
    from pydeseq2.dds import DeseqDataSet
    from pydeseq2.ds import DeseqStats
    rename = functools.partial(re.sub,pattern="_",repl="-",count=0)
    renames = np.vectorize(rename,otypes=[str])
    case=rename(string=case)
    ref=rename(string=ref)
    pdata["Condition"]=renames(string=pdata.iloc[:,0])
    pdata = pdata.loc[pdata.Condition.isin([ref,case]),:]
    common_sample = np.intersect1d(fdata.index,pdata.index)
    fdata = fdata.loc[common_sample,:]
    pdata = pdata.loc[common_sample,:]
    pdata["Condition"] = pdata.Condition.astype('category').values
    genes_to_keep = fdata.columns[fdata.sum(axis=0) >= 10]
    fdata = fdata[genes_to_keep]
    inference=pydeseq2.default_inference.DefaultInference(joblib_verbosity=0, n_cpus=n_jobs)
    dds = DeseqDataSet(
        counts=fdata,
        metadata=pdata,
        ref_level=["Condition", ref],
        design_factors="Condition",
        refit_cooks=True,
        inference=inference
    )
    # 离散度和log fold-change评估.
    dds.deseq2()
    # 差异表达统计检验分析
    stat_res = DeseqStats(
        dds,
        alpha=0.05,
        cooks_filter=True,
        contrast=['Condition', case, ref],
        independent_filter=True,
        inference=inference
    )
    stat_res.summary()
    return stat_res.results_df.reset_index().rename(
        columns=dict(
            Gene="Feature", log2FoldChange="LFC", padj="Padj", pvalue="Pvalue"
        )
    )
    

def geneIDconverter(frame, from_id='Ensembl', to_id='Symbol',species="hsa", keep_from=False, gene_type=None):
    if species == "hsa":
        file_path = "h38_gene_info_v43.csv.gz"
    if species == "mmu":
        file_path = "m39_gene_info_v32.csv.gz"
    annot = _IO.read_csv_gz(file_path)
    if from_id=='Ensembl':
        annot.loc[:,"Ensembl"] = bq.st.removes(string=annot.Ensembl,pattern=r"\.\d+")
    annot.set_index(keys=from_id,inplace=True,drop=True)
    if gene_type:
        gene_type = annot.GeneType.isin(gene_type)
        annot = annot.loc[gene_type:, [to_id]]
    else:
        annot = annot.loc[:, [to_id]]
    if keep_from:
        annoted = pd.merge(annot, frame, left_index=True, right_index=True)
    else:
        annoted = pd.merge(annot, frame, left_index=True, right_index=True)
        annoted.set_index(keys=to_id, inplace=True)
    return annoted

def countto(frame, towhat="tpm", geneid='Ensembl', species="hsa"):
    '''
    towhat: tpm(default), fpkm, cpm
    return: a dataframe
    '''
    from bioinfokit import analys
    if species == "hsa":
        file_path = "h38_gene_info_v43.csv.gz"
    if species == "mmu":
        file_path = "m39_gene_info_v32.csv.gz"
    annot = read_csv_gz(file_path, usecols=[
                        geneid, 'Length'])
    if geneid=='Ensembl':
        annot.loc[:,"Ensembl"] = bq.st.removes(string=annot.Ensembl,pattern=r"\.\d+")
    annot.set_index(keys=geneid,inplace=True,drop=True)
    _df = pd.merge(annot, frame, left_index=True, right_index=True)
    nm = analys.norm()
    nm.tpm(df=_df, gl='Length')
    nm.rpkm(df=_df, gl='Length')
    nm.cpm(df=_df)
    if towhat=="tpm":
        return nm.tpm_norm
    if towhat=="fpkm":
        return nm.rpkm_norm
    if towhat=="cpm":
        return nm.cpm_norm.drop(columns="Length")
