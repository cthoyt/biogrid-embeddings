import pathlib
import zipfile

import bioversions
import click
import humanize
import networkx as nx
import pystow
from more_click import verbose_option
from nodevectors import Node2Vec
from tqdm import tqdm

from utils import echo, save_tabbed_word2vec_format

HERE = pathlib.Path(__file__).parent.resolve()


def _iter(file):
    lines = (
        line.decode("utf-8").strip().split("\t")
        for line in tqdm(
            file, unit_scale=True, unit="interaction", desc="Preparing graph"
        )
    )

    header = next(lines)
    header_dict = {entry: i for i, entry in enumerate(header)}

    source_key = header_dict["SWISS-PROT Accessions Interactor A"]
    target_key = header_dict["SWISS-PROT Accessions Interactor B"]
    organism_a_key = header_dict["Organism Name Interactor A"]
    organism_b_key = header_dict["Organism Name Interactor B"]

    for line in lines:
        if (
            line[organism_a_key] != "Homo sapiens"
            or line[organism_b_key] != "Homo sapiens"
        ):
            continue
        a, b = line[source_key], line[target_key]
        if not a or not b or a == "-" or b == "-":
            continue
        yield a, b


@click.command()
@verbose_option
def main():
    version = bioversions.get_version("biogrid")
    module = pystow.module("bio", "biogrid", version)

    url = (
        f"https://downloads.thebiogrid.org/Download/BioGRID/Release-Archive/"
        f"BIOGRID-{version}/BIOGRID-ALL-{version}.tab3.zip"
    )

    path = module.ensure(url=url)
    with zipfile.ZipFile(path) as zip_file:
        with zip_file.open(f"BIOGRID-ALL-{version}.tab3.txt") as file:
            graph = nx.Graph(_iter(file))

    echo("Getting largest connected components")
    nodes = sorted(nx.connected_components(graph), key=len, reverse=True)[0]
    echo(f"Largest connected component has {humanize.intword(len(nodes))} " "nodes")
    echo("Inducing subgraph")
    giant = graph.subgraph(nodes)
    echo("Copying subgraph")
    giant = giant.copy()
    echo(
        "Done inducing subgraph. Has "
        f"{humanize.intword(giant.number_of_nodes())} "
        f"nodes and {humanize.intword(giant.number_of_edges())} edges"
    )

    node2vec = Node2Vec(
        n_components=64,
        return_weight=2.3,  # from SEffNet
        neighbor_weight=1.9,  # from SEffNet
        walklen=8,  # from SEffNet
        epochs=8,  # from SEffNet
        w2vparams={
            "window": 4,  # from SEffNet
            "negative": 5,  # default
            "iter": 10,  # default
            # default from gensim,
            # see https://github.com/VHRanger/nodevectors/issues/34
            "batch_words": 10000,
        },
        verbose=True,
        keep_walks=False,
    )

    tqdm.write("fitting model")
    node2vec.fit(giant)  # takes about 5-8 minutes
    tqdm.write("fit model")

    output = HERE.joinpath("output", version)
    output.mkdir(exist_ok=True, parents=True)

    save_tabbed_word2vec_format(
        wv=node2vec.model.wv,
        vectors_path=output.joinpath("embeddings.tsv"),
        vocab_path=output.joinpath("vocab.tsv"),
    )


if __name__ == "__main__":
    main()
