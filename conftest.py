import unittest
import pytest


def run_tagger(content, *fns):
    """Run a tagger function, return region tags that got applied"""
    from clictagger.region.utils import regions_flatten

    book = dict(content=content)
    for fn in fns:
        fn(book)
    return regions_flatten(book)


@pytest.fixture(autouse=True)
def doctest_extras(doctest_namespace):
    # Add extras to the namespace
    doctest_namespace["run_tagger"] = run_tagger
    yield doctest_namespace
