"""Plot infrastructure namespace, without plot-specific statistical functions."""

from ..export import imagesave, save
from ..fonts import fontcheck, fontinfo, fontlist, register_font, setfont
from ..palettes import Palette, colormap, palette
from ..presets import FigurePreset, figure_preset, preset_names
from ..themes import theme, theme_params

__all__ = [
    "FigurePreset",
    "Palette",
    "colormap",
    "figure_preset",
    "fontcheck",
    "fontinfo",
    "fontlist",
    "imagesave",
    "palette",
    "preset_names",
    "register_font",
    "save",
    "setfont",
    "theme",
    "theme_params",
]
