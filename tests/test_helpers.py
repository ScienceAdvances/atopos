"""Exercise palette boundaries, immutable presets, and legacy backup integrity."""

import hashlib
import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

import atopos


def test_presets_are_immutable_and_customization_is_independent():
    original = atopos.figure_preset("single_column")
    customized = atopos.figure_preset(original, height=75, formats="svg")
    assert original.height == 65
    assert customized.height == 75
    assert customized.formats == ("svg",)
    with pytest.raises(FrozenInstanceError):
        original.dpi = 600


def test_palette_boundaries_and_historical_colors():
    assert atopos.palette("DARK2") == atopos.Palette.set2
    assert atopos.palette("set2") != atopos.Palette.set2
    assert atopos.palette("dark2", reverse=True) == atopos.palette("dark2")[::-1]
    with pytest.raises(ValueError, match="only"):
        atopos.palette("dark2", n=9)
    assert len(atopos.palette("dark2", n=16, interpolate=True)) == 16
    assert atopos.colormap("economist")(0)


def test_mkdir_returns_absolute_path(tmp_path):
    path = atopos.mkdir(tmp_path / "nested" / "output")
    assert path.is_absolute() and path.is_dir()
    assert atopos.tl.mkdir(path) == path


def test_original_backup_matches_recorded_checksums():
    legacy = Path(__file__).resolve().parents[1] / "legacy"
    if not legacy.exists():
        pytest.skip("The historical backup is intentionally excluded from distributions.")
    manifest = json.loads((legacy / "SHA256SUMS.json").read_text())
    assert len(manifest) == 21
    for name, digest in manifest.items():
        content = (legacy / "atopos-1.0.0" / name).read_bytes()
        assert hashlib.sha256(content).hexdigest() == digest, name
