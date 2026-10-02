# atopos

Fonts, scoped themes, palettes, and unified figure export for scientific workflows.

Version 2 focuses on plotting infrastructure shared by analysis packages.
Gene mapping, normalization, differential expression, ROC/calibration, forest
plots, and dataframe/string helpers are preserved in [legacy/](legacy/README.md)
for migration and excluded from the new distribution.

## Install

```sh
pip install atopos
```

For this unreleased checkout, use `pip install -e .`. Matplotlib is the only
runtime dependency. Seaborn and plotnine remain optional.

## Create and export

```python
import matplotlib.pyplot as plt
import atopos

with atopos.theme(font="DejaVu Sans", palette="okabe_ito", fontsize=9):
    fig, ax = plt.subplots(layout="constrained")
    ax.plot([0, 1, 2], [1, 3, 2], label="Measurement")
    ax.set(xlabel="Time", ylabel="Value")
    ax.legend()
    paths = atopos.imagesave(
        fig,
        "measurement",
        outdir="figures",
        preset="single_column",
        formats=("pdf", "svg", "png", "tiff"),
        dpi=600,
    )

print(paths["pdf"])
plt.close(fig)
```

Create figures inside the theme block. Global settings restore on exit, including
on errors. Export retains the figure and restores its original size and fonts.
Use a live layout engine such as `layout="constrained"` when resizing to presets,
so labels and margins are recalculated at the export size. A one-time
`fig.tight_layout()` before resizing does not reserve new margins automatically.
SVG keeps text as text, so other viewers may require the same fonts. PDF uses
TrueType embedding where supported by the font and backend.

## Unified export

`imagesave()` (also `save()`) accepts a Matplotlib Figure or Axes, a Seaborn grid
with a `.figure`/`.fig`, an object whose `draw()` returns a Figure (such as
plotnine), or a zero-argument plotting callable returning a Figure/Axes or drawing
the current figure. `None` uses an existing current figure; an empty session
raises an error. Axes within a SubFigure export the root Figure.

```python
paths = atopos.save(ax, "panel.png", outdir="figures", overwrite=False)
paths = atopos.save(
    fig,
    "panel",
    outdir="figures",
    formats=("pdf", "png"),
    width=85,
    height=60,
    units="mm",
    dpi=300,
)
```

| Argument | Behavior |
| --- | --- |
| `outdir` | Required, non-empty directory; created when needed. |
| `name` | Filename stem or supported extension; directory components rejected. |
| `formats` | PDF, SVG, PNG, JPG/JPEG, TIF/TIFF; aliases normalized and duplicates removed. |
| `preset` | Built-in name or FigurePreset; explicit options take precedence. |
| `width`, `height`, `units` | Physical size in `in`, `cm`, or `mm`; without a preset, omitted dimensions retain figure size. |
| `dpi` | Raster resolution, default 300; vector elements stay vector in PDF/SVG. |
| `bg`, `transparent` | Background color or transparency; JPEG requires an opaque background. |
| `quality`, `compression` | JPEG quality 0–100; TIFF `lzw`, `deflate`, `packbits`, or `none`. |
| `font` | Temporarily apply an available font to existing text during export. |
| `bbox_inches` | Default None preserves canvas dimensions; `"tight"` crops them. |
| `overwrite`, `close` | Default: overwrite files and retain the figure. |

Without a preset, the default format is PDF. A recognized extension in `name`
selects the format when `formats` is omitted, even with a preset. With a preset,
`units` applies to explicit dimensions; omitted dimensions keep the preset's
physical size. Returns canonical format names mapped to absolute pathlib.Paths.

Each format is rendered from the original figure. All requested renders finish
before destination files change; each file replacement is atomic. This is not
a transaction across multiple files: filesystem failures during final replacement
can leave a partially updated set. `overwrite=False` checks all destinations
before drawing and refuses collisions during file creation.

## Presets

| Preset | Width × height | DPI | Formats |
| --- | --- | --- | --- |
| `publication` | 150 × 110 mm | 300 | PDF, PNG |
| `single_column` | 85 × 65 mm | 300 | PDF, PNG |
| `double_column` | 180 × 120 mm | 300 | PDF, PNG |
| `high_resolution` | 150 × 110 mm | 600 | PDF, PNG |
| `presentation` | 160 × 90 mm | 150 | PNG |

```python
preset = atopos.figure_preset("single_column", height=75, dpi=600)
atopos.imagesave(fig, "custom", outdir="figures", preset=preset)
```

Presets are starting points; compare them with the journal's current instructions.

## Fonts and scoped themes

```python
families = atopos.fontlist("Arial|Noto|DejaVu")
available = atopos.fontcheck("Arial")
info = atopos.fontinfo("DejaVu Sans", text="Measurement ± 1")
print(info.path, info.missing_characters)

# Register a local font for this process, without a system-wide installation.
# family = atopos.register_font("/path/to/font.ttf")

with atopos.setfont("Arial", fallback="DejaVu Sans"):
    fig, ax = plt.subplots()
    ax.set_title("Temporary font")

with atopos.theme(style="presentation", grid=True, rc={"lines.linewidth": 2}):
    fig, ax = plt.subplots()
```

Missing fonts raise an error unless an explicit fallback is supplied, which
produces a warning. `fontcheck(..., text=..., error=True)` rejects missing glyphs.
Diagnostics inspect the resolved regular face, not every weight or fallback.
`setfont()` affects newly created text; export's `font` applies to existing text.

Theme options: `style`, `font`, `fallback`, `fontsize`, `palette`, `grid`, and `rc`.
`theme_params()` returns the rc dictionary for other packages. Scoped themes
reject backend overrides because Matplotlib does not restore backend changes.

## Palettes and directories

```python
names = atopos.palette()
colors = atopos.palette("okabe_ito", n=4)
cmap = atopos.colormap("economist")
directory = atopos.mkdir("figures/supplement")
```

Palettes: `okabe_ito`, `economist`, `dark2`, and `set2`, matched case-insensitively.
Too many discrete colors raise an error. Use `interpolate=True` for continuous
scales. No colormap is registered globally.

## Migration and compatibility

This is a major-version change. Removed functionality remains in the legacy
snapshot, including original data, license, dependencies, and known-defect notes.

`atopos.tl.mkdir`, `atopos.tl.saveimg`, and `atopos.pl.Palette` remain available:

```python
save = atopos.tl.saveimg(("pdf", "png"), outdir="figures")
paths = save(filename="panel")
```

The deprecated save factory now retains the figure, restores settings, and
actually applies figsize to the exported image. Its omitted output directory
still defaults to the working directory. Historical Palette.set2 values are
preserved (they were actually Dark2); palette("set2") supplies genuine Set2.

## Development

```sh
pip install -e '.[dev]'
ruff check .
ruff format --check .
MPLBACKEND=Agg python -m pytest
python -m build
```

The legacy snapshot is excluded from wheels and source distributions. See
examples/publication.py for a complete export example.
