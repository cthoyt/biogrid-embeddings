import pathlib
import pickle
import zipfile

import bioversions
import click
import networkx as nx
import pystow
from more_click import verbose_option
from more_node2vec import fit_model, process_graph
from tqdm import tqdm


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

    giant = process_graph(graph)
    model = fit_model(giant)

    output = HERE.joinpath("output", version)
    output.mkdir(exist_ok=True, parents=True)
    model.save(output)

    wv = model.wv
    with output.joinpath("embeddings.pkl").open("wb") as file:
        pickle.dump(dict(zip(wv.vocab, wv.vectors)), file)


if __name__ == "__main__":
    main()
