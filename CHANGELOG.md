# Changelog

## 2.0.0 (unreleased)

- Focus on fonts, themes, palettes, presets, directories, and unified figure export.
- Preserve the exact original checkout in legacy/ with SHA-256 checksums; remove
  domain-specific analysis, ROC/calibration, forest, dataframe, and string functions.
- Add direct PDF/SVG/PNG/JPEG/TIFF export, plot adapters, physical dimensions,
  presets, collision protection, returned paths, and figure-state restoration.
- Add font discovery, regular-face glyph diagnostics, session registration,
  and scoped font/publication/presentation contexts.
- Add palettes and opt-in interpolation, preserving the original Palette class.
- Retain deprecated tl.saveimg and tl.mkdir; saving retains figures and restores
  original dimensions and global settings.
- Reduce runtime dependencies to Matplotlib; add tests, examples, CI, migration docs.
