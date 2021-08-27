import pathlib
import zipfile

import bioversions
import click
import matplotlib.pyplot as plt
import networkx as nx
import pystow
from more_click import force_option, verbose_option
from more_node2vec import Model, echo, fit_model, process_graph
from tqdm import tqdm

HERE = pathlib.Path(__file__).parent.resolve()
MODULE = pystow.module("bio", "biogrid")
VOCAB_NAME = "vocab.tsv"
VECTOR_NAME = "embeddings.tsv"


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
@force_option
def main(force: bool):
    """Generate network-based embeddings for each protein."""
    # Get the current version of BioGRID using :mod:`bioversions`.
    version = bioversions.get_version("biogrid")

    # Create a version-specific output directory
    output = HERE.joinpath("output", version)
    output.mkdir(exist_ok=True, parents=True)

    if output.joinpath("embeddings.pkl").is_file() and not force:
        echo("loading model")
        model = Model.load(output, vocab_name=VOCAB_NAME, vector_name=VECTOR_NAME)
    else:
        url = (
            f"https://downloads.thebiogrid.org/Download/BioGRID/Release-Archive/"
            f"BIOGRID-{version}/BIOGRID-ALL-{version}.tab3.zip"
        )

        path = MODULE.ensure(version, url=url)
        with zipfile.ZipFile(path) as zip_file:
            with zip_file.open(f"BIOGRID-ALL-{version}.tab3.txt") as file:
                graph = nx.Graph(_iter(file))

        processed_graph = process_graph(graph)
        model = fit_model(processed_graph)
        model.save(
            output, vocab_name=VOCAB_NAME, vector_name=VECTOR_NAME, save_dict=True
        )

    fig, _ = model.plot_pca()
    fig.tight_layout()
    fig.savefig(output.joinpath("scatter.svg"))
    plt.close(fig)


if __name__ == "__main__":
    main()
