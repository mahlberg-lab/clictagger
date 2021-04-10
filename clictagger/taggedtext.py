"""
clictagger.taggedtext: Region-tag text
**************************************

The TaggedText class is the main python interface to clictagger.
You can use it to import a string of text, and print out a summary of regions::

    >>> from clictagger.taggedtext import TaggedText
    >>> tt = TaggedText('''
    ... The Dove in the Eagle's Nest
    ... Charlotte M. Yonge
    ...
    ... “Thou find’st it out, child?  Ay, ’tis worth all the feather-beds and\r
    ... pouncet-boxes in Ulm; is it not?  That accursed Italian fever never left
    ... me till I came up here.  A man can scarce draw breath in your foggy
    ... meadows below there.  Now then, ‘here is the view open.’  What think you of
    ... the Eagle’s Nest?”
    ... '''.lstrip())
    >>> print(tt)
    TaggedText: The Dove in the Eagle's Nest
        characters=355
        metadata.title=1
        metadata.author=1
        chapter.text=1
        chapter.paragraph=1
        chapter.sentence=6
        quote.quote=1
        quote.embedded=1
        tokens=65

You can also import text from a file::

    >>> tt = TaggedText.from_file('alice.txt')
    >>> print(tt)
    TaggedText: alice.txt
        characters=144396
        metadata.title=1
        metadata.author=1
        chapter.title=12
        chapter.text=12
        chapter.paragraph=804
        chapter.sentence=1674
        quote.quote=1098
        quote.embedded=47
        quote.nonquote=865
        quote.suspension.short=166
        quote.suspension.long=106
        tokens=26548

... or from a github repository::

    >>> tt = TaggedText.from_github("ChiLit/alice.txt", repo="birmingham-ccr/corpora", tag="80d00e4")
    >>> print(tt)
    TaggedText: https://raw.githubusercontent.com/birmingham-ccr/corpora/80d00e4/ChiLit/alice.txt
        characters=144396
        metadata.title=1
        metadata.author=1
        chapter.title=12
        chapter.text=12
        chapter.paragraph=804
        chapter.sentence=1674
        quote.quote=1098
        quote.embedded=47
        quote.nonquote=865
        quote.suspension.short=166
        quote.suspension.long=106
        tokens=26548

"""
import sys

from .tokenizer import tagger_tokens
from .region.metadata import tagger_metadata
from .region.chapter import tagger_chapter
from .region.quote import tagger_quote
from .region.suspension import tagger_quote_suspension

from .markup import TaggedTextRegionMarkup
from .table import TaggedTextRegionTable


DEFAULT_HIGHLIGHT_REGIONS = [
    "metadata.title",
    "metadata.author",
    "chapter.sentence",
    "quote.quote",
    "quote.suspension.short",
    "quote.suspension.long",
    "chapter.title",
]


class TaggedText:
    """
    Initialise a TaggedText object from a string.

    - content: The string containing the content to tag
    - name: A descriptive name, if not given, and one is found, the "metadata.title" region is used
    """

    def __init__(self, content, name=None):
        book = dict(content=content)
        tagger_metadata(book)
        tagger_chapter(book)
        tagger_quote(book)
        tagger_quote_suspension(book)
        tagger_tokens(book)
        del book["content"]

        if name is None and len(book.get("metadata.title", [])) > 0:
            # If no name, but have a title, extract that
            self.name = content[
                book["metadata.title"][0][0] : book["metadata.title"][0][1]
            ]
        else:
            self.name = name
        self.content = content
        self.regions = book

    @classmethod
    def from_file(cls, text_path):
        """
        Initialise a TaggedText object from a file.

        - text_path: The path of the file to read. Should be a UTF-8 encoded file
        """
        if text_path == "-":
            return cls(sys.stdin.read(), name="stdin")
        with open(text_path, "r") as f:
            return cls(f.read(), name=text_path)

    @classmethod
    def from_github(cls, file_path, repo="birmingham-ccr/corpora", tag="HEAD"):
        """
        Initialise a TaggedText object from a github repository

        - file_path: Path to the file within the repository
        - repo: The repo name & organisation, defaults to "birmingham-ccr/corpora"
        - tag: The branch/tag/version to download, defaults to "HEAD"

        For example::

            TaggedText.from_github("ChiLit/alice.txt", tag = "80d00e4")
        """

        if repo == "birmingham-ccr/corpora" and not file_path.endswith(".txt"):
            file_path += ".txt"
        return cls.from_url(
            "/".join(("https://raw.githubusercontent.com", repo, tag, file_path))
        )

    @classmethod
    def from_url(cls, url):
        """
        Initialise a TaggedText object from a URL

        - url: URL pointing at the UTF-8 encoded file to read

        For example::

            TaggedText.from_url("http://www.gutenberg.org/files/36/36-0.txt")
        """
        import urllib.request

        with urllib.request.urlopen(url) as f:
            return cls(f.read().decode("utf8"), name=url)

    def __str__(self):
        str_parts = [
            ("characters", len(self.content)),
        ]
        for rclass in self.regions.keys():
            if len(self.regions[rclass]) > 0:
                str_parts.append((rclass, len(self.regions[rclass])))
        return "TaggedText: %s%s" % (
            self.name or "",
            "".join("\n    %s=%s" % p for p in str_parts),
        )

    def _repr_html_(self):
        # https://ipython.readthedocs.io/en/stable/config/integrating.html
        str_parts = [
            ("characters", len(self.content)),
        ]
        for rclass in self.regions.keys():
            if len(self.regions[rclass]) > 0:
                str_parts.append((rclass, len(self.regions[rclass])))
        return "<b>TaggedText:</b>%s<table>%s</table>" % (
            self.name or "",
            "".join("<tr><th>%s</th><td>%s</td></tr>" % p for p in str_parts),
        )

    def __html__(self):
        """Inform other modules we are HTML safe"""
        # https://github.com/ipython/ipython/blob/master/IPython/core/display.py#L419
        return self._repr_html_()

    def region_classes(self):
        """Return a list of all region classes searched for in the document"""
        return list(self.regions.keys())

    def markup(self, highlight=DEFAULT_HIGHLIGHT_REGIONS):
        """
        Return a TaggedTextRegionMarkup object for displaying text with region tags highlighted

        - highlight: List of region tag classes to highlight
        """
        if len(highlight) == 0:
            highlight = DEFAULT_HIGHLIGHT_REGIONS
        return TaggedTextRegionMarkup(self, highlight)

    def table(self, highlight=DEFAULT_HIGHLIGHT_REGIONS, display="html"):
        """
        Return a TaggedTextRegionTable object for displaying region tags in tables

        - highlight: List of region tag classes to highlight
        """
        if len(highlight) == 0:
            highlight = DEFAULT_HIGHLIGHT_REGIONS
        return TaggedTextRegionTable(self, highlight, display=display)
