# Profile collapsing

The **profile collapsing** function is a lightweight and flexible addition to the main classification workflow. It allows the user to convert an _existing_ profile based on a mapping of source features to target features. It highlights the support for **many-to-many mapping**.

```bash
woltka tools collapse -i input.biom -m mapping.txt -o output.biom
```

With this tool one can achieve the following goals:

1. Translate feature IDs into names or descriptions.
   - Example: Translate taxonomic IDs to taxon names.
   - Example: Translate [UniRef](https://www.uniprot.org/help/uniref) IDs to protein names, while **merging** same names.

2. Group lower features into higher categories.
   - Example: Convert genera to families.

3. Convert lower features into higher ones, where each lower feature may correspond to **multiple** higher features.
   - Example: Convert KEGG [orthologs](https://www.genome.jp/kegg/ko.html) to [pathways](https://www.genome.jp/kegg/pathway.html).
   - Example: Convert [GO](http://geneontology.org/docs/ontology-documentation/) terms to [GO Slim](http://www-legacy.geneontology.org/GO.slims.shtml) terms.

The last usage is an important complement to the main classification workflow, which currently relies on a tree structure and does not support one-to-many mapping. This can be achieved by using the profile collapsing function (although one can only move up one level per run).


## Mapping file format

A mapping file is a text file with entries separated by tabs. The number of fields per line is _arbitrary_. The first field is the source feature ID. The second to last fields are target feature ID(s). Duplicates in sources or targets are allowed. For examples:

1. One/many-to-one:
```
source1 <tab> target1
source2 <tab> target2
source3 <tab> target2
source4 <tab> target3
...
```

2. Many-to-many (multiple targets per line):
```
source1 <tab> target1
source2 <tab> target1 <tab> target2
source3 <tab> target2 <tab> target3 <tab> target4
...
```

3. Many-to-many (multiple same sources):
```
source1 <tab> target1
source1 <tab> target2
source2 <tab> target2
source3 <tab> target3
source4 <tab> target3
...
```

## Parameters

### Normalization

By default, if one source feature is simultaneously mapped to _k_ targets, each target will be counted once. With the `--normalize` or `-z` flag added to the command, each target will be counted 1 / _k_ times.

Whether to enable normalization depends on the nature and aim of your analysis. For example, one gene is involved in two pathways (which isn't uncommon), should each pathway be counted once, or half time?

### Feature names

Once a profile is collapsed, the metadata of the source features ("Name", "Rank", and "Lineage") will be discarded. One may choose to supply a target feature name file by `--names` or `-n`, which will instruct the program to append names to the profile as a metadata column ("Name").
