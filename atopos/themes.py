"""Scoped publication themes; importing atopos never installs a global style."""

from matplotlib import cycler, rc_context

from .fonts import resolve_font
from .palettes import palette as get_palette
from .presets import positive_number


def theme_params(
    *,
    style="publication",
    font="DejaVu Sans",
    fallback=None,
    fontsize=None,
    palette="okabe_ito",
    grid=False,
    rc=None,
):
    """Return Matplotlib rc parameters for a publication or presentation theme.

    Overrides in ``rc`` take precedence. Backend changes are deliberately rejected
    because Matplotlib does not restore the backend on rc_context exit.
    """
    if style not in {"publication", "presentation"}:
        raise ValueError("style must be 'publication' or 'presentation'.")
    size = positive_number(
        fontsize if fontsize is not None else (9 if style == "publication" else 14), "fontsize"
    )
    colors = get_palette(palette) if isinstance(palette, str) else tuple(palette)
    if not colors:
        raise ValueError("palette must contain at least one color.")
    params = {
        "font.family": [resolve_font(font, fallback)],
        "font.size": size,
        "axes.labelsize": size,
        "axes.titlesize": size + 1,
        "axes.titleweight": "normal",
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.prop_cycle": cycler(color=colors),
        "axes.grid": grid,
        "axes.axisbelow": True,
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "lines.linewidth": 1.2,
        "lines.markersize": 4,
        "xtick.labelsize": size - 1,
        "ytick.labelsize": size - 1,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "grid.linewidth": 0.4,
        "grid.alpha": 0.3,
        "legend.fontsize": size - 1,
        "legend.frameon": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }
    if rc:
        if "backend" in rc:
            raise ValueError("A scoped theme cannot change the Matplotlib backend.")
        params.update(rc)
    return params


def theme(**kwargs):
    """Return a temporary theme: ``with theme(...): ...``.

    Create figures inside the block. Settings restore on exit, including errors;
    the function never changes the properties of existing plot objects.
    """
    return rc_context(theme_params(**kwargs))
