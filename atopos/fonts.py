"""Font discovery, glyph diagnostics, and temporary font configuration."""

import re
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from matplotlib import font_manager, ft2font, rc_context


@dataclass(frozen=True)
class FontInfo:
    family: str
    path: Optional[Path]
    missing_characters: Tuple[str, ...] = ()

    @property
    def available(self):
        return self.path is not None


def fontlist(pattern=None):
    """List installed and session-registered font families."""
    families = sorted({entry.name for entry in font_manager.fontManager.ttflist})
    if pattern is not None:
        regex = re.compile(pattern, re.IGNORECASE)
        families = [family for family in families if regex.search(family)]
    return families


def fontinfo(family="DejaVu Sans", *, text=""):
    """Resolve a family without silent fallback and optionally inspect glyphs.

    Generic families such as ``sans-serif`` resolve through Matplotlib's current
    configuration. Glyph checks inspect the resolved regular face only.
    """
    if not isinstance(family, str) or not family.strip():
        raise ValueError("family must be a non-empty string.")
    if not isinstance(text, str):
        raise TypeError("text must be a string.")
    try:
        path = Path(
            font_manager.findfont(
                font_manager.FontProperties(family=[family]), fallback_to_default=False
            )
        )
    except ValueError:
        return FontInfo(family, None)
    if not path.is_file():
        return FontInfo(family, None)
    missing = ()
    if text:
        glyphs = ft2font.FT2Font(str(path)).get_charmap()
        missing = tuple(
            sorted({char for char in text if not char.isspace() and ord(char) not in glyphs})
        )
    return FontInfo(family, path, missing)


def fontcheck(family="DejaVu Sans", *, text="", error=False):
    """Check font availability and optional character coverage."""
    info = fontinfo(family, text=text)
    valid = info.available and not info.missing_characters
    if error and not valid:
        if not info.available:
            raise ValueError(f"Font {family!r} is unavailable. Use fontlist() or register_font().")
        raise ValueError(f"Font {family!r} is missing characters: {info.missing_characters!r}.")
    return valid


def resolve_font(family, fallback=None):
    if fontcheck(family):
        return family
    if fallback is None:
        fontcheck(family, error=True)
    fontcheck(fallback, error=True)
    warnings.warn(f"Font {family!r} is unavailable; using {fallback!r}.", UserWarning, stacklevel=2)
    return fallback


def register_font(path):
    """Register a font file for this Python process and return its family name."""
    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    font_manager.fontManager.addfont(str(path))
    return font_manager.FontProperties(fname=str(path)).get_name()


def setfont(family="DejaVu Sans", *, fallback=None):
    """Return a font context for text created inside a ``with`` block.

    Existing text artists are unchanged; ``imagesave(font=...)`` can temporarily
    apply a font to an existing figure during export.
    """
    return rc_context({"font.family": [resolve_font(family, fallback)]})
