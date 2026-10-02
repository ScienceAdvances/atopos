"""Fonts, themes, palettes, and export infrastructure for scientific figures."""

__version__ = "2.0.0"

from . import pl, tl
from .export import imagesave, save, saveimg
from .fonts import FontInfo, fontcheck, fontinfo, fontlist, register_font, setfont
from .palettes import Palette, colormap, palette
from .presets import FigurePreset, figure_preset, preset_names
from .themes import theme, theme_params
from .utils import mkdir

__all__ = [
    "FigurePreset",
    "FontInfo",
    "Palette",
    "colormap",
    "figure_preset",
    "fontcheck",
    "fontinfo",
    "fontlist",
    "imagesave",
    "mkdir",
    "palette",
    "pl",
    "preset_names",
    "register_font",
    "save",
    "saveimg",
    "setfont",
    "theme",
    "theme_params",
    "tl",
]
