import unittest
import pytest
import re


def display(obj):
    """Fake IPython.display for tests"""
    content = obj.__html__()
    content = re.sub(r"<style>[^<]+</style>", "", content)
    content = re.sub(r'<ul class="legend">.+</ul>', "", content)
    # Remove containing divs, since they'll have random IDs in
    content = re.sub(r"<div[^<]+>", "", content)
    content = re.sub(r"</div>", "", content)
    # Remove useless <span>
    content = re.sub(r"</span><span>", "", content)
    content = re.sub(r"<span></span>", "", content)
    print(content)


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
    doctest_namespace["display"] = display
    doctest_namespace["run_tagger"] = run_tagger
    yield doctest_namespace
