"""Named palettes shared by themes and plotting libraries."""

from matplotlib.colors import LinearSegmentedColormap, to_hex

_PALETTES = {
    "economist": (
        "#6794a7",
        "#014d64",
        "#01a2d9",
        "#7ad2f6",
        "#00887d",
        "#76c0c1",
        "#7c260b",
        "#ee8f71",
        "#adadad",
    ),
    "dark2": (
        "#1B9E77",
        "#D95F02",
        "#7570B3",
        "#E7298A",
        "#66A61E",
        "#E6AB02",
        "#A6761D",
        "#666666",
    ),
    "set2": (
        "#66c2a5",
        "#fc8d62",
        "#8da0cb",
        "#e78ac3",
        "#a6d854",
        "#ffd92f",
        "#e5c494",
        "#b3b3b3",
    ),
    "okabe_ito": (
        "#0072B2",
        "#E69F00",
        "#009E73",
        "#D55E00",
        "#CC79A7",
        "#56B4E9",
        "#F0E442",
        "#000000",
    ),
}


def palette(name=None, n=None, *, reverse=False, interpolate=False):
    """List palette names or return colors.

    Requests beyond the palette size fail unless interpolation is explicitly
    enabled. Interpolation is intended for continuous scales, not new categories.
    """
    if name is None:
        return tuple(_PALETTES)
    try:
        colors = _PALETTES[name.lower()]
    except (KeyError, AttributeError):
        raise ValueError(f"Unknown palette {name!r}. Choose from {tuple(_PALETTES)}.") from None
    if reverse:
        colors = colors[::-1]
    if n is None:
        return colors
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer.")
    if interpolate:
        cmap = LinearSegmentedColormap.from_list(str(name), colors, N=max(n, 2))
        return tuple(to_hex(cmap(i / max(n - 1, 1))) for i in range(n))
    if n > len(colors):
        raise ValueError(f"Palette {name!r} contains only {len(colors)} discrete colors.")
    return colors[:n]


def colormap(name="okabe_ito", *, reverse=False):
    """Create a Matplotlib colormap without registering it globally."""
    return LinearSegmentedColormap.from_list(name, palette(name, reverse=reverse))


class Palette:
    """Compatibility colors from atopos 1.x.

    The historical ``set2`` attribute actually contains Dark2 colors and is
    retained unchanged. Use ``palette('set2')`` for the genuine Set2 palette.
    """

    economist = _PALETTES["economist"]
    set2 = _PALETTES["dark2"]
