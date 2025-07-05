import functools
import gzip
from typing import Tuple, Union

import matplotlib.pyplot as plt
import pandas as pd
from importlib import resources
from typing import Union
import pathlib

from .. import _data


def _output(filename: str, _format: str, *, outdir: Union[pathlib.PosixPath,str] = pathlib.Path().absolute()) -> pathlib.PosixPath:
    if isinstance(outdir,str):
        return pathlib.Path(outdir).joinpath(f"{filename}.{_format}")
    elif isinstance(outdir,pathlib.PosixPath):
        return outdir.joinpath(f"{filename}.{_format}")
    else:
        raise ValueError(f'{outdir} should be string or pathlib.PosixPath class')


def _saveimg(
    filename: str,
    formats: Union[str, Tuple[str, ...]],
    *,
    outdir: Union[pathlib.PosixPath,str] = pathlib.Path().absolute(),
    dpi: int = 300,
    figsize=(7, 7),
) -> None:
    if isinstance(formats, str):
        formats = (formats,)

    plt.rcParams["figure.figsize"] = figsize
    for i in formats:
        plt.savefig(
            _output(filename=filename, _format=i, outdir=outdir),
            dpi=dpi,
            bbox_inches="tight",
        )
    plt.close()


def saveimg(
    formats: Union[str, Tuple[str, ...]],
    *,
    outdir: Union[pathlib.PosixPath,str] = pathlib.Path().absolute(),
    dpi: int = 300,
    figsize=(7, 7),
):
    return functools.partial(
        _saveimg, formats=formats, outdir=outdir, dpi=dpi, figsize=figsize
    )


def mkdir(dir: str, parents=True, exist_ok=True):
    pathlib.Path(dir).mkdir(parents=parents, exist_ok=exist_ok)


def read_csv_gz(
    data_file_name: str,
    index_col=None,
    usecols=None,
    sep=",",
    *,
    encoding="utf-8",
    **kwargs,
):
    """Loads gzip-compressed with `importlib.resources`.

    1) Open resource file with `importlib.resources.open_binary`
    2) Decompress file obj with `gzip.open`
    3) Load decompressed data with `pd.read_csv`

    Parameters
    ----------
    data_file_name : str
            Name of gzip-compressed csv file  (`'*.csv.gz'`) to be loaded from
            `_data/data_file_name`. For example `'humanGene.csv.gz'`.
    """

    with resources.open_binary(_data, data_file_name) as _:
        _ = gzip.open(_, mode="rt", encoding=encoding)
        _df = pd.read_csv(_, usecols=usecols, index_col=index_col, sep=sep)
    return _df
