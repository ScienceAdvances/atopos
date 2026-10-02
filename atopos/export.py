"""Export original plot objects directly to vector and raster formats."""

import os
import warnings
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from matplotlib import rc_context
from matplotlib.axes import Axes
from matplotlib.colors import is_color_like, to_rgba
from matplotlib.figure import Figure
from matplotlib.text import Text

from .fonts import resolve_font
from .presets import figure_preset, inches, positive_number

_FORMATS = {
    "pdf": "pdf",
    "svg": "svg",
    "png": "png",
    "jpg": "jpg",
    "jpeg": "jpg",
    "tif": "tiff",
    "tiff": "tiff",
}
_COMPRESSION = {
    "lzw": "tiff_lzw",
    "tiff_lzw": "tiff_lzw",
    "none": "raw",
    "raw": "raw",
    "deflate": "tiff_adobe_deflate",
    "tiff_adobe_deflate": "tiff_adobe_deflate",
    "packbits": "packbits",
}


def _formats(value):
    if isinstance(value, str):
        value = (value,)
    try:
        values = tuple(value)
    except TypeError:
        raise ValueError("formats must be a format name or an iterable of names.") from None
    if not values:
        raise ValueError("formats must not be empty.")
    result = []
    for item in values:
        try:
            normalized = _FORMATS[item.lower().lstrip(".")]
        except (KeyError, AttributeError):
            raise ValueError(
                f"Unsupported format {item!r}. Choose PDF, SVG, PNG, JPEG, or TIFF."
            ) from None
        if normalized not in result:
            result.append(normalized)
    return tuple(result)


def _figure(plot):
    if plot is None:
        import matplotlib.pyplot as plt

        if not plt.get_fignums():
            raise ValueError(
                "No current figure exists. Pass a plot object or create a figure first."
            )
        return plt.gcf()
    if isinstance(plot, Figure):
        return plot
    if isinstance(plot, Axes):
        # The root Figure owns export even when the Axes lives in a SubFigure.
        parent = plot.figure
        while not isinstance(parent, Figure):
            parent = parent.figure
        return parent
    for attr in ("figure", "fig"):
        candidate = getattr(plot, attr, None)
        if isinstance(candidate, Figure):
            return candidate
    draw = getattr(plot, "draw", None)
    if not callable(draw) and not callable(plot):
        raise TypeError("plot must be a Figure, Axes, figure-bearing object, or plotting callable.")
    import matplotlib.pyplot as plt

    before = set(plt.get_fignums())
    try:
        result = draw() if callable(draw) else plot()
        if result is plot:
            raise TypeError("The plotting callable must return a figure, axes, or None.")
        return _figure(result)
    except BaseException:
        # A failed draw must not leave new pyplot windows behind.
        for number in set(plt.get_fignums()) - before:
            plt.close(number)
        raise


@contextmanager
def _figure_state(fig, width, height, font):
    size = fig.get_size_inches().copy()
    text_props = []
    try:
        if width is not None or height is not None:
            fig.set_size_inches(
                width if width is not None else size[0],
                height if height is not None else size[1],
                forward=False,
            )
        if font is not None:
            # Materialize lazy tick labels before collecting the text artists.
            fig.canvas.draw()
            for text in fig.findobj(match=Text):
                original = text.get_fontproperties().copy()
                props = original.copy()
                props.set_family([font])
                text_props.append((text, original))
                text.set_fontproperties(props)
        yield
    finally:
        fig.set_size_inches(*size, forward=False)
        for text, props in text_props:
            text.set_fontproperties(props)


def imagesave(
    plot=None,
    name="plot",
    *,
    outdir,
    formats=None,
    preset=None,
    width=None,
    height=None,
    units=None,
    dpi=None,
    bg=None,
    transparent=False,
    quality=None,
    compression=None,
    bbox_inches=None,
    pad_inches=0.1,
    font=None,
    overwrite=True,
    close=False,
):
    """Save one plot to PDF, SVG, PNG, JPEG, and/or TIFF; return a path dictionary.

    ``plot`` accepts a Matplotlib Figure/Axes, a Seaborn grid, an object whose
    ``draw()`` returns a Figure (for example plotnine), or a zero-argument plotting
    callable. None uses an existing current figure without creating a blank one.

    ``outdir`` is required. Dimensions use in/cm/mm. Without a preset, omitted
    dimensions retain the figure size; with a preset, explicit dimensions override
    its physical size. ``units`` applies to explicit dimensions only. Exact output
    size is preserved by default; ``bbox_inches='tight'`` crops the canvas.

    Every format is rendered from the original figure. All renders finish before
    destination files are replaced, and each replacement is atomic. Existing
    figures, fonts, and rc settings restore on failure as well as success. Figures
    remain open unless ``close=True``. No plot-specific analysis is performed.
    """
    if not isinstance(name, (str, os.PathLike)):
        raise TypeError("name must be a filename stem.")
    name = os.fspath(name)
    if (
        not isinstance(name, str)
        or not name.strip()
        or name in {".", ".."}
        or "/" in name
        or "\\" in name
    ):
        raise ValueError("name must be a non-empty filename, without directory components.")
    suffix = Path(name).suffix.lower().lstrip(".")
    inferred = _FORMATS.get(suffix)
    stem = name[: -(len(suffix) + 1)] if inferred else name
    if not stem.strip():
        raise ValueError("name must include a filename stem.")
    if outdir is None or (isinstance(outdir, str) and not outdir.strip()):
        raise ValueError("An explicit, non-empty outdir is required.")
    directory = Path(outdir).expanduser().resolve()
    settings = figure_preset(preset) if preset is not None else None
    selected = _formats(
        formats
        if formats is not None
        else ((inferred,) if inferred else (settings.formats if settings else ("pdf",)))
    )
    units = units if units is not None else (settings.units if settings else "in")
    # Validate units even when no explicit dimensions were provided.
    inches(1, units)
    w = (
        inches(width, units)
        if width is not None
        else (inches(settings.width, settings.units) if settings else None)
    )
    h = (
        inches(height, units)
        if height is not None
        else (inches(settings.height, settings.units) if settings else None)
    )
    resolution = positive_number(
        dpi if dpi is not None else (settings.dpi if settings else 300), "dpi"
    )
    background = bg if bg is not None else (settings.bg if settings else "white")
    if not is_color_like(background):
        raise ValueError("bg must be a valid Matplotlib color.")
    if "jpg" in selected and (transparent or to_rgba(background)[3] < 1):
        raise ValueError("JPEG cannot preserve transparency. Choose an opaque bg or PNG/TIFF.")
    jpeg_quality = quality if quality is not None else (settings.quality if settings else 95)
    if (
        isinstance(jpeg_quality, bool)
        or not isinstance(jpeg_quality, int)
        or not 0 <= jpeg_quality <= 100
    ):
        raise ValueError("quality must be an integer between 0 and 100.")
    tiff_compression = (
        compression if compression is not None else (settings.compression if settings else "lzw")
    )
    if tiff_compression not in _COMPRESSION:
        raise ValueError(f"Unsupported TIFF compression {tiff_compression!r}.")
    if bbox_inches not in (None, "tight"):
        raise ValueError("bbox_inches must be None or 'tight'.")
    if isinstance(pad_inches, bool) or not isinstance(pad_inches, (int, float)) or pad_inches < 0:
        raise ValueError("pad_inches must be a finite, non-negative number.")
    if pad_inches != 0:
        positive_number(pad_inches, "pad_inches")
    family = resolve_font(font) if font is not None else None
    paths = {fmt: directory / f"{stem}.{fmt}" for fmt in selected}
    for path in paths.values():
        if path.is_dir():
            raise IsADirectoryError(path)
        if not overwrite and path.exists():
            raise FileExistsError(path)
    rc = {
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "savefig.bbox": bbox_inches,
    }
    if family is not None:
        rc["font.family"] = [family]
    with rc_context(rc):
        fig = _figure(plot)
        directory.mkdir(parents=True, exist_ok=True)
        with _figure_state(fig, w, h, family):
            with TemporaryDirectory(prefix=".atopos-", dir=directory) as staging:
                rendered = {}
                for fmt, path in paths.items():
                    temporary = Path(staging) / path.name
                    options = {}
                    if fmt == "jpg":
                        options["pil_kwargs"] = {"quality": jpeg_quality}
                    elif fmt == "tiff":
                        options["pil_kwargs"] = {"compression": _COMPRESSION[tiff_compression]}
                    fig.savefig(
                        temporary,
                        format=fmt,
                        dpi=resolution,
                        facecolor="none" if transparent else background,
                        transparent=transparent,
                        bbox_inches=bbox_inches,
                        pad_inches=pad_inches,
                        **options,
                    )
                    rendered[fmt] = temporary
                for fmt, path in paths.items():
                    if overwrite:
                        os.replace(rendered[fmt], path)
                    else:
                        # Hard linking refuses a file that appeared after preflight.
                        os.link(rendered[fmt], path)
    if close:
        import matplotlib.pyplot as plt

        plt.close(fig)
    return paths


save = imagesave


def saveimg(formats, *, outdir=None, dpi=300, figsize=None):
    """Compatibility factory for ``atopos.tl.saveimg(...)(filename=...)``.

    Prefer imagesave(). The old factory still uses the current working directory
    when outdir is omitted, but now retains the figure and restores settings.
    """
    warnings.warn(
        "saveimg() is deprecated; use imagesave(plot, name, outdir=...).",
        DeprecationWarning,
        stacklevel=2,
    )
    directory = Path.cwd() if outdir is None else outdir
    if figsize is not None and len(figsize) != 2:
        raise ValueError("figsize must contain width and height in inches.")

    def save_current(filename, *, plot=None):
        return imagesave(
            plot,
            filename,
            outdir=directory,
            formats=formats,
            dpi=dpi,
            width=figsize[0] if figsize is not None else None,
            height=figsize[1] if figsize is not None else None,
        )

    return save_current
