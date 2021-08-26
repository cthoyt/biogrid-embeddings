# biogrid-node2vec

This repository generates node2vec embeddings for physical molecular interactions in
[BioGRID](https://thebiogrid.org/).

## 🚀 Usage

Installation of the requirements and running of the build script are handled with `tox`. The current
version of BioGRID is looked up with [`bioversions`](https://github.com/cthoyt/bioversions) so the
provenance of the data can be properly traced. Run with:

```shell
$ pip install tox
$ tox
```

The embedding dataframe can be loaded from GitHub with:

```python
import pandas as pd

url = "https://github.com/cthoyt/biogrid-node2vec/raw/main/output/4.4.200/embeddings.tsv"
df = pd.read_csv(url, sep="\t", skiprows=1)
```

The index uses [UniProt](https://bioregistry.io/uniprot) protein identifiers. It skips a line since
this TSV file uses the word2vec format, where the first line says the length and width of the file.

## ⚖️ License

Code in this repository is licensed under the MIT License.

## 🙏 Acknowledgements

BioGRID can be cited with:

```bibtex
@article{Oughtred2021,
    author = {Oughtred, Rose and Rust, Jennifer and Chang, Christie and Breitkreutz, Bobby-Joe and Stark, Chris and Willems, Andrew and Boucher, Lorrie and Leung, Genie and Kolas, Nadine and Zhang, Frederick and Dolma, Sonam and Coulombe-Huntington, Jasmin and Chatr-Aryamontri, Andrew and Dolinski, Kara and Tyers, Mike},
    doi = {10.1002/pro.3978},
    journal = {Protein science : a publication of the Protein Society},
    keywords = {COVID-19,CRISPR screen,biological network,chemical interaction,drug target,genetic interaction,phenotype,post-translational modification,protein interaction,ubiquitin-proteasome system},
    number = {1},
    pages = {187--200},
    pmid = {33070389},
    title = {{The BioGRID database: A comprehensive biomedical resource of curated protein, genetic, and chemical interactions.}},
    volume = {30},
    year = {2021}
}
```
