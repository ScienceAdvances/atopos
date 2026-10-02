"""Check font diagnosis and temporary styles across success and exceptions."""

import subprocess
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest

import atopos


def test_font_availability_and_missing_glyphs():
    assert atopos.fontcheck("DejaVu Sans", text="Measurement ± 1")
    assert atopos.fontcheck("sans-serif")
    assert not atopos.fontcheck("Atopos Missing Font 846b09")
    info = atopos.fontinfo("DejaVu Sans", text="A\U0010ffff\U0010ffff")
    assert info.path.is_file()
    assert info.missing_characters == ("\U0010ffff",)
    with pytest.raises(ValueError, match="missing characters"):
        atopos.fontcheck("DejaVu Sans", text="\U0010ffff", error=True)
    with pytest.raises(ValueError, match="unavailable"):
        atopos.fontcheck("Atopos Missing Font 846b09", error=True)
    assert "DejaVu Sans" in atopos.fontlist("dejavu")


def test_register_font_is_process_local(monkeypatch):
    from matplotlib import font_manager

    monkeypatch.setattr(
        font_manager.fontManager, "ttflist", font_manager.fontManager.ttflist.copy()
    )
    path = atopos.fontinfo("DejaVu Sans").path
    assert atopos.register_font(path) == "DejaVu Sans"


def test_scoped_theme_restores_after_exception_and_nested_font():
    rc = mpl.rcParams.copy()
    try:
        with pytest.raises(RuntimeError):
            with atopos.theme(fontsize=10, palette="dark2", grid=True):
                assert mpl.rcParams["font.size"] == 10
                assert mpl.rcParams["axes.grid"]
                with atopos.setfont("DejaVu Serif"):
                    assert mpl.rcParams["font.family"] == ["DejaVu Serif"]
                    fig, ax = plt.subplots()
                    text = ax.set_title("Scoped title")
                    assert text.get_fontfamily() == ["DejaVu Serif"]
                assert mpl.rcParams["font.family"] == ["DejaVu Sans"]
                raise RuntimeError("Simulated analysis error")
        assert dict(mpl.rcParams) == dict(rc)
    finally:
        plt.close("all")


def test_missing_font_fallback_is_explicit():
    rc = mpl.rcParams.copy()
    with pytest.warns(UserWarning, match="using"):
        with atopos.setfont("Atopos Missing Font 846b09", fallback="DejaVu Sans"):
            assert mpl.rcParams["font.family"] == ["DejaVu Sans"]
    assert dict(mpl.rcParams) == dict(rc)


def test_theme_rejects_backend_changes_and_invalid_styles():
    with pytest.raises(ValueError, match="backend"):
        atopos.theme(rc={"backend": "svg"})
    with pytest.raises(ValueError, match="style"):
        atopos.theme(style="unknown")


def test_import_has_no_analysis_dependencies_or_global_style_effects():
    code = """
import sys
import matplotlib as mpl
before = mpl.rcParams.copy()
import atopos
assert dict(before) == dict(mpl.rcParams)
assert not any(name in sys.modules for name in ('pandas', 'sklearn', 'scipy', 'bioinfokit', 'seaborn'))
assert not hasattr(atopos, 'ml')
assert not hasattr(atopos, 'st')
assert not hasattr(atopos.pl, 'forest_plot')
assert not hasattr(atopos.tl, 'deseq')
"""
    subprocess.run([sys.executable, "-c", code], check=True)
