# Merging profiles

The **merge** command merges two or more profiles into one, while treating overlapping samples and features in an additive way. This is useful when the analysis includes multiple sets of input files (e.g., multiple sequencing runs).

```bash
woltka tools merge -i input1.biom -i input2.biom -i input3.biom -o output.biom
```

The output file from the merge command is **identical** or nearly identical to the output file generated by merging sequence alignment file prior to running Woltka. Small errors (differring by the count of **1**) could be introduced during the normalization of _multiple assignments_ due to floating point arithmetic issues, which is usually not troublesome. In addition to sticking to one-to-one alignments, one can use classification parameters `--rank free`, `--uniq`, `--major`, or `--above` to prevent small errors ([see details](classify.md#ambiguous-assignment)).