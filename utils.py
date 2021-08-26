from __future__ import annotations

import csv
import datetime
import gzip
from contextlib import contextmanager
from pathlib import Path
from typing import Union

import click
from gensim.models.keyedvectors import Word2VecKeyedVectors


def save_tabbed_word2vec_format(
    *,
    wv: Word2VecKeyedVectors,
    vectors_path: Union[str, Path],
    vocab_path: Union[str, Path],
) -> None:
    """Save the word2vec format."""
    sorted_vocab_items = sorted(
        wv.vocab.items(), key=lambda item: item[1].count, reverse=True
    )
    total_vec = len(wv.vocab)
    vectors = wv.vectors
    vector_size = vectors.shape[1]
    if total_vec != vectors.shape[0]:
        raise ValueError

    with writer(vectors_path) as vectors_writer, writer(vocab_path) as vocab_writer:
        vectors_writer.writerow((total_vec, vector_size))
        for word, vocab_ in sorted_vocab_items:
            # Write to vocab file
            vocab_writer.writerow((word, vocab_.count))
            # Write to vectors file
            vector_row = word, *(repr(val) for val in vectors[vocab_.index])
            vectors_writer.writerow(vector_row)


@contextmanager
def writer(path: Union[str, Path]):
    """Open a CSV writer context manager."""
    opener, kwargs = _get_writer(path)
    with opener(path, **kwargs) as file:
        yield csv.writer(file, delimiter="\t", quoting=csv.QUOTE_MINIMAL)


def _get_writer(path: Union[str, Path]):
    """Get the file opener."""
    if isinstance(path, str):
        path = Path(path)
    if path.suffix == ".gz":
        return gzip.open, dict(mode="wt")
    return open, {"mode": "w"}


@contextmanager
def reader(path: Union[str, Path]):
    """Open a CSV reader context manager."""
    opener, kwargs = _get_reader(path)
    with opener(path, **kwargs) as file:
        yield csv.reader(file, delimiter="\t", quoting=csv.QUOTE_MINIMAL)


def _get_reader(path: Union[str, Path]):
    if isinstance(path, str):
        path = Path(path)
    if path.suffix == ".gz":
        return gzip.open, {"mode": "rt"}
    return open, {"mode": "r"}


def echo(*s, sep=" ", **kwargs):
    """Write with :func:`click.secho` preceed by the time."""
    time_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    log_str = sep.join(str(x) for x in s)
    click.echo(
        click.style(f"[{time_str}] ", fg="blue") + click.style(log_str, **kwargs)
    )
