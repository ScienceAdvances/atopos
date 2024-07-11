import numpy as np
import pathlib
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from ..pl._palette import Palette
from ..tl._IO import saveimg
from typing import Tuple, Union

def ROC(y_true:dict, y_hat:dict,xlabel=None,ylabel=None, outdir=None,filename=''):
    """
    plot multiple ROC curves in one figure
    y_true: dict
    y_hat: dict
    outdir: output directory
    filename: filename
    """
    from sklearn.metrics import RocCurveDisplay
    colors = dict(zip(y_hat,Palette.set2))
    for i in y_hat.keys():
        RocCurveDisplay.from_predictions(y_true[i], y_hat[i], name = i, color= colors[i], ax=plt.gca(),linewidth=2)
    plt.plot([0,1],[0,1], linestyle="dashed",color = "grey");
    if ylabel:
        plt.ylabel(ylabel)
    else:
        plt.ylabel("True Positive Rate");
    if xlabel:
        plt.xlabel(xlabel);
    else:
        plt.xlabel("False Positive Rate");
    p = plt.gcf()
    p.set_size_inches(6, 6)
    plt.close()
    if outdir:
        p.savefig(pathlib(outdir).joinpath(f"{filename}.pdf"))
    return p

def CC(
    y_true:dict,
    y_hat:dict,
    outdir: Union[pathlib.PosixPath,str] = pathlib.Path().absolute(),
    filename:str='CalibrationCurve') -> Figure:
    """
    y_true: dict
    y_hat: dict
    outdir: output directory
    filename: filename
    """
    from sklearn.calibration import CalibrationDisplay
    from sklearn.preprocessing import MinMaxScaler
    colors = dict(zip(y_hat,Palette.set2))
    if any(y_hat.min()<0) or any(y_hat.max()>0):
        y = MinMaxScaler((.0000000001,.9999999999)).fit_transform(y_hat)
    else:
        y = y_hat.values
    for i in y_hat.keys():
        CalibrationDisplay.from_predictions(y_true[i], y_hat[i], name = i, color= colors[i], ax=plt.gca(),linewidth=2)
    plt.plot([0,1],[0,1], linestyle="dashed",color = "grey");
    plt.ylabel("True Positive Rate");
    plt.xlabel("False Positive Rate");
    p = plt.gcf()
    p.set_size_inches(6, 6)
    plt.close()
    if outdir:
        p.savefig(pathlib(outdir).joinpath(f"{filename}.pdf"))
    return p

# def learning_curve(x,xlabel='',ylabel='',mark:int=0, outdir:str=None) -> Figure :
#     plt.rc('axes', labelsize=16) #fontsize of the x and y labels
#     plt.rc('xtick', labelsize=12) #fontsize of the x tick labels
#     plt.rc('ytick', labelsize=12)
#     plt.plot(np.arange(mark, len(x)+mark), 
#         x,
#         color='grey', 
#         linewidth=.8,
#         # linestyle='dashed', 
#         marker='o',
#         markerfacecolor='white',
#         markeredgecolor='r',
#         markersize=5
#         )
#     plt.plot(np.where(x==x.max())[0] + mark,
#         x.max(),
#         marker='o',
#         markerfacecolor='white',
#         markersize=10,
#         markeredgecolor='b'
#         )
#     plt.gca().spines.right.set_visible(False)
#     plt.gca().spines.top.set_visible(False)
#     plt.ylabel(ylabel)
#     plt.xlabel(xlabel)
#     p = plt.gcf()
#     p.set_size_inches(9, 6)
#     plt.close()
#     if outdir:
#         p.savefig(outdir + "/LearningCurve"+ ".pdf",dpi=300)
#     return p
