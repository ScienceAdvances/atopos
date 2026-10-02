"""Verify real rendered outputs and figure state, including failure paths."""

import re
from types import SimpleNamespace
from xml.etree import ElementTree

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest
from PIL import Image

import atopos


@pytest.fixture(autouse=True)
def isolated_figures():
    with mpl.rc_context():
        plt.close("all")
        yield
        plt.close("all")


@pytest.fixture
def figure():
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.plot([0, 1, 2], [1, 3, 2], label="Signal")
    ax.set(xlabel="Time", ylabel="Value", title="Export test")
    return fig


def test_real_formats_dimensions_and_restoration(figure, tmp_path):
    original_size = tuple(figure.get_size_inches())
    original_rc = mpl.rcParams.copy()
    paths = atopos.imagesave(
        figure,
        "sample",
        outdir=tmp_path,
        formats=("pdf", "svg", "png", "jpeg", "tif"),
        width=50.8,
        height=25.4,
        units="mm",
        dpi=100,
    )
    assert tuple(paths) == ("pdf", "svg", "png", "jpg", "tiff")
    assert all(path.is_absolute() and path.stat().st_size > 0 for path in paths.values())
    for fmt in ("png", "jpg", "tiff"):
        with Image.open(paths[fmt]) as image:
            assert image.size == (200, 100)
            assert image.getbbox() is not None
    with Image.open(paths["tiff"]) as image:
        assert image.info["compression"] == "tiff_lzw"
    pdf = paths["pdf"].read_bytes()
    assert pdf.startswith(b"%PDF")
    match = re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]", pdf)
    assert tuple(float(value) for value in match.groups()) == pytest.approx((144, 72))
    assert b"/FontFile2" in pdf
    assert b"/Subtype /Image" not in pdf
    svg = ElementTree.parse(paths["svg"]).getroot()
    assert [float(v) for v in svg.attrib["viewBox"].split()] == pytest.approx([0, 0, 144, 72])
    assert svg.findall(".//{http://www.w3.org/2000/svg}text")
    assert not svg.findall(".//{http://www.w3.org/2000/svg}image")
    assert tuple(figure.get_size_inches()) == original_size
    assert plt.fignum_exists(figure.number)
    assert dict(mpl.rcParams) == dict(original_rc)


def test_preset_override_keeps_omitted_physical_dimension(figure, tmp_path):
    preset = atopos.figure_preset("single_column", height=25.4, dpi=100)
    paths = atopos.save(figure, "custom.png", outdir=tmp_path, preset=preset, width=2, units="in")
    assert tuple(paths) == ("png",)
    with Image.open(paths["png"]) as image:
        assert image.size == (200, 100)


def test_no_dimensions_preserve_canvas(figure, tmp_path):
    # A caller's global tight-crop default must not override physical dimensions.
    mpl.rcParams["savefig.bbox"] = "tight"
    paths = atopos.save(figure, "original", outdir=tmp_path, formats="png", dpi=100)
    with Image.open(paths["png"]) as image:
        assert image.size == (400, 300)
    assert mpl.rcParams["savefig.bbox"] == "tight"


@pytest.mark.parametrize(
    "adapter",
    [
        lambda fig: fig.axes[0],
        lambda fig: SimpleNamespace(figure=fig),
        lambda fig: SimpleNamespace(fig=fig),
        lambda fig: SimpleNamespace(draw=lambda: fig),
        lambda fig: lambda: fig,
    ],
)
def test_plot_object_adapters(figure, tmp_path, adapter):
    paths = atopos.save(adapter(figure), "adapter", outdir=tmp_path)
    assert paths["pdf"].read_bytes().startswith(b"%PDF")


def test_current_figure_is_not_confused_with_explicit_figure(figure, tmp_path):
    other = plt.figure(figsize=(1, 1))
    paths = atopos.save(figure.axes[0], "explicit", outdir=tmp_path, formats="png", dpi=100)
    with Image.open(paths["png"]) as image:
        assert image.size == (400, 300)
    assert plt.gcf() is other
    paths = atopos.save(name="current.png", outdir=tmp_path, dpi=100)
    with Image.open(paths["png"]) as image:
        assert image.size == (100, 100)


def test_subfigure_axes_export_root(tmp_path):
    fig = plt.figure(figsize=(4, 2))
    subfig = fig.subfigures(1, 2)[0]
    ax = subfig.subplots()
    ax.plot([0, 1])
    paths = atopos.save(ax, "root.png", outdir=tmp_path, dpi=100)
    with Image.open(paths["png"]) as image:
        assert image.size == (400, 200)


def test_empty_session_never_creates_blank_figure(tmp_path):
    with pytest.raises(ValueError, match="No current figure"):
        atopos.save(outdir=tmp_path / "new")
    assert not plt.get_fignums()
    assert not (tmp_path / "new").exists()


def test_plotting_callable_restores_rc_and_failed_draw_windows(figure, tmp_path):
    rc = mpl.rcParams.copy()
    before = plt.get_fignums()

    def failed_draw():
        mpl.rcParams["font.size"] = 37
        plt.figure()
        raise RuntimeError("Simulated drawing failure")

    with pytest.raises(RuntimeError, match="drawing failure"):
        atopos.save(failed_draw, outdir=tmp_path / "new")
    assert dict(mpl.rcParams) == dict(rc)
    assert plt.get_fignums() == before
    assert not (tmp_path / "new").exists()


def test_plotting_callable_that_returns_none(tmp_path):
    def draw():
        mpl.rcParams["font.size"] = 17
        plt.figure(figsize=(2, 1))
        plt.plot([0, 1])

    original_size = mpl.rcParams["font.size"]
    paths = atopos.save(draw, "callable.png", outdir=tmp_path, dpi=100, close=True)
    assert mpl.rcParams["font.size"] == original_size
    with Image.open(paths["png"]) as image:
        assert image.size == (200, 100)
    assert not plt.get_fignums()


def test_collision_preflight_preserves_all_files(figure, tmp_path):
    existing = tmp_path / "sample.png"
    existing.write_bytes(b"original")
    with pytest.raises(FileExistsError):
        atopos.save(figure, "sample", outdir=tmp_path, formats=("pdf", "png"), overwrite=False)
    assert existing.read_bytes() == b"original"
    assert not (tmp_path / "sample.pdf").exists()


def test_render_failure_preserves_files_fonts_size_and_rc(figure, tmp_path, monkeypatch):
    existing = tmp_path / "sample.pdf"
    existing.write_bytes(b"original")
    title = figure.axes[0].title
    title.set_fontfamily("DejaVu Serif")
    family = title.get_fontfamily()
    size = tuple(figure.get_size_inches())
    rc = mpl.rcParams.copy()
    savefig = figure.savefig

    def fail_second(path, **kwargs):
        if kwargs["format"] == "png":
            raise RuntimeError("Simulated rendering failure")
        return savefig(path, **kwargs)

    monkeypatch.setattr(figure, "savefig", fail_second)
    with pytest.raises(RuntimeError, match="Simulated"):
        atopos.save(
            figure,
            "sample",
            outdir=tmp_path,
            formats=("pdf", "png"),
            width=2,
            height=1,
            font="DejaVu Sans",
        )
    assert existing.read_bytes() == b"original"
    assert not (tmp_path / "sample.png").exists()
    assert not list(tmp_path.glob(".atopos-*"))
    assert tuple(figure.get_size_inches()) == size
    assert title.get_fontfamily() == family
    assert dict(mpl.rcParams) == dict(rc)
    assert plt.fignum_exists(figure.number)


def test_transparency_and_explicit_close(figure, tmp_path):
    paths = atopos.save(figure, "alpha.png", outdir=tmp_path, transparent=True, close=True)
    with Image.open(paths["png"]) as image:
        assert image.mode == "RGBA"
        assert image.getpixel((0, 0))[3] == 0
    assert not plt.fignum_exists(figure.number)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"formats": "gif"},
        {"formats": []},
        {"width": 0},
        {"height": float("nan")},
        {"units": "px"},
        {"dpi": float("inf")},
        {"quality": 101},
        {"compression": "invalid"},
        {"bg": "invalid-color"},
        {"formats": "jpg", "transparent": True},
        {"pad_inches": float("nan")},
        {"font": "Atopos Missing Font 846b09"},
    ],
)
def test_invalid_export_options_do_not_write(figure, tmp_path, kwargs):
    with pytest.raises(ValueError):
        atopos.save(figure, "invalid", outdir=tmp_path / "new", **kwargs)
    assert not (tmp_path / "new").exists()


@pytest.mark.parametrize("name", ["", " ", "../escape", "folder/name", "folder\\name"])
def test_filename_rejects_directory_components(figure, tmp_path, name):
    with pytest.raises(ValueError):
        atopos.save(figure, name, outdir=tmp_path)


@pytest.mark.parametrize("outdir", [None, "", " "])
def test_output_directory_is_explicit(figure, outdir):
    with pytest.raises(ValueError):
        atopos.save(figure, outdir=outdir)


def test_duplicate_aliases_and_legacy_factory(figure, tmp_path):
    with pytest.warns(DeprecationWarning):
        save = atopos.tl.saveimg(("png", ".PNG"), outdir=tmp_path, dpi=100, figsize=(2, 1))
    paths = save(filename="legacy")
    assert tuple(paths) == ("png",)
    with Image.open(paths["png"]) as image:
        assert image.size == (200, 100)
    assert tuple(figure.get_size_inches()) == (4, 3)
    assert plt.fignum_exists(figure.number)
