"""Reusable physical dimensions and rendering settings for scientific figures."""

from dataclasses import dataclass, replace
from math import isfinite
from typing import Tuple


def positive_number(value, name):
    """Validate a positive, finite dimension or resolution."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a positive finite number.")
    if not isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive finite number.")
    return float(value)


def inches(value, units):
    factors = {"in": 1.0, "cm": 2.54, "mm": 25.4}
    if units not in factors:
        raise ValueError("units must be 'in', 'cm', or 'mm'.")
    return positive_number(value, "dimension") / factors[units]


@dataclass(frozen=True)
class FigurePreset:
    """An immutable export preset; explicit export arguments override it."""

    name: str = "publication"
    width: float = 150
    height: float = 110
    units: str = "mm"
    dpi: float = 300
    formats: Tuple[str, ...] = ("pdf", "png")
    bg: str = "white"
    quality: int = 95
    compression: str = "lzw"

    def __post_init__(self):
        inches(self.width, self.units)
        inches(self.height, self.units)
        positive_number(self.dpi, "dpi")
        if isinstance(self.formats, str):
            object.__setattr__(self, "formats", (self.formats,))
        else:
            object.__setattr__(self, "formats", tuple(self.formats))
        if not self.formats:
            raise ValueError("formats must not be empty.")


_PRESETS = {
    "publication": FigurePreset(),
    "single_column": FigurePreset("single_column", width=85, height=65),
    "double_column": FigurePreset("double_column", width=180, height=120),
    "high_resolution": FigurePreset("high_resolution", dpi=600),
    "presentation": FigurePreset("presentation", width=160, height=90, dpi=150, formats=("png",)),
}


def figure_preset(name="publication", **overrides):
    """Return a built-in or customized preset, without changing global settings.

    These dimensions are starting points, not guarantees of journal compliance.
    """
    if isinstance(name, FigurePreset):
        preset = name
    else:
        try:
            preset = _PRESETS[name]
        except (KeyError, TypeError):
            raise ValueError(f"Unknown preset {name!r}. Choose from {tuple(_PRESETS)}.") from None
    return replace(preset, **overrides) if overrides else preset


def preset_names():
    """Return the available built-in preset names."""
    return tuple(_PRESETS)
