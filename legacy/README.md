# atopos 1.0.0 source backup

atopos-1.0.0/ preserves every tracked file from the original checkout before the
version 2 refactor: source, annotation tables, Apache license, README, dependency
configuration, and release workflow. It is excluded from the new distributions.

SHA256SUMS.json records each original file's SHA-256, relative to atopos-1.0.0/.
The snapshot comes from commit bc81127 with a clean working tree. All copied files
were verified byte for byte.

## Reuse in another package

Copy relevant modules/data into the destination package, preserve license notices,
and adapt relative imports and resource loading to its namespace:

- atopos/tl/gene.py: gene IDs, significance labels, normalization, and DESeq2.
- atopos/tl/utils.py: expression deduplication and TCGA helpers.
- atopos/tl/_frame.py and atopos/st/: dataframe and string helpers.
- atopos/_data/: original human and mouse annotation tables.
- atopos/ml/ and atopos/pl/forest.py: ROC, calibration, and forest plots.

This is historical source, not a maintained replacement. Its package name is still
atopos; do not install it alongside version 2. PyDESeq2 and pyarrow were used but
not declared in the original dependency configuration.

## Known defects to address before reuse

- Gene conversion references undefined _IO and has an invalid gene-type selector.
- Normalization strips Ensembl versions only from annotations and discards unmatched
  genes even for CPM, changing its denominator.
- Significance relabeling preserves stale labels.
- subset(inplace=True) does not modify input; string conditions use eval.
- Symbol conversion can lose unmatched indices; deduplication modifies input.
- Calibration's dictionary interface is broken; ROC uses obsolete sklearn drawing
  parameters and an incorrect pathlib(...) output call.
- Plotting has figure lifecycle, size, and palette-limit defects.
- DESeq2 mutates metadata, assumes its first column is the condition, and uses
  deprecated design arguments.

The archived source is unchanged; fixes belong in receiving packages.
