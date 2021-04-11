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

You can use the :py:meth:`TaggedText.markup` or :py:meth:`TaggedText.table` methods to present the tagged regions.
Both classes are compatible with `Juypter notebooks <https://jupyter.org/>`__, and can
by pretty printed by IPython using ``IPython.display``::

    >>> # from IPython.display import display
    >>> tt = TaggedText('''‘Well!’ thought Alice to herself, ‘after such a fall as this, I shall think nothing of tumbling down stairs!’''')
    >>> display(tt.markup())
    <span title="chapter.paragraph:1 chapter.sentence:1 chapter.text:0 quote.quote" class="chapter-paragraph chapter-sentence chapter-text quote-quote">‘Well!’</span><span class="chapter-sentence-close"></span><span title="chapter.paragraph:1 chapter.text:0" class="chapter-paragraph chapter-text"> </span><span title="chapter.paragraph:1 chapter.text:0 chapter.sentence:2 quote.nonquote quote.suspension.short" class="chapter-paragraph chapter-text chapter-sentence quote-nonquote quote-suspension-short">thought Alice to herself,</span><span title="chapter.paragraph:1 chapter.text:0 chapter.sentence:2" class="chapter-paragraph chapter-text chapter-sentence"> </span><span title="chapter.paragraph:1 chapter.text:0 chapter.sentence:2 quote.quote" class="chapter-paragraph chapter-text chapter-sentence quote-quote">‘after such a fall as this, I shall think nothing of tumbling down stairs!’</span><span class="chapter-sentence-close"></span>
    >>> display(tt.table())
    <table>
    <tr><th>Region class</th><th>Start</th><th>End</th><th>Region value</th><th>Content</th></tr>
    <tr><td>chapter.sentence</td> <td>0</td> <td>7</td> <td>1</td> <td style="text-align: left">‘Well!’</td></tr>
    <tr><td>chapter.sentence</td> <td>8</td> <td>109</td> <td>2</td> <td style="text-align: left">thought Alice to herself, ‘after such a fall as this, I shall think nothing of tumbling down stairs!’</td></tr>
    <tr><td>quote.quote</td> <td>0</td> <td>7</td> <td></td> <td style="text-align: left">‘Well!’</td></tr>
    <tr><td>quote.quote</td> <td>34</td> <td>109</td> <td></td> <td style="text-align: left">‘after such a fall as this, I shall think nothing of tumbling down stairs!’</td></tr>
    <tr><td>quote.suspension.short</td> <td>8</td> <td>33</td> <td></td> <td style="text-align: left">thought Alice to herself,</td></tr>
    </table>

The :py:meth:`TaggedText.table` method also supports generating a CSV download link::

    >>> display(tt.table(display="csv-download"))
    <a download="regions.csv" href="data:text/csv;base64,IlJlZ2lvbiBjbGFzcyIsIlN0YXJ0IiwiRW5kIiwiUmVnaW9uIHZhbHVlIiwiQ29udGVudCINCmNoYXB0ZXIuc2VudGVuY2UsMCw3LCIxIiwi4oCYV2VsbCHigJkiDQpjaGFwdGVyLnNlbnRlbmNlLDgsMTA5LCIyIiwidGhvdWdodCBBbGljZSB0byBoZXJzZWxmLCDigJhhZnRlciBzdWNoIGEgZmFsbCBhcyB0aGlzLCBJIHNoYWxsIHRoaW5rIG5vdGhpbmcgb2YgdHVtYmxpbmcgZG93biBzdGFpcnMh4oCZIg0KcXVvdGUucXVvdGUsMCw3LCIiLCLigJhXZWxsIeKAmSINCnF1b3RlLnF1b3RlLDM0LDEwOSwiIiwi4oCYYWZ0ZXIgc3VjaCBhIGZhbGwgYXMgdGhpcywgSSBzaGFsbCB0aGluayBub3RoaW5nIG9mIHR1bWJsaW5nIGRvd24gc3RhaXJzIeKAmSINCnF1b3RlLnN1c3BlbnNpb24uc2hvcnQsOCwzMywiIiwidGhvdWdodCBBbGljZSB0byBoZXJzZWxmLCINCg==" target="_blank">Download regions.csv</a>
"""
import base64
import collections
import sys

from .tokenizer import tagger_tokens
from .region.metadata import tagger_metadata
from .region.chapter import tagger_chapter
from .region.quote import tagger_quote
from .region.suspension import tagger_quote_suspension

from .markup import _gen_markup_ansi, _gen_markup_html
from .table import _gen_table_csv, _gen_table_html


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
        with open(text_path, "r", encoding="utf8") as f:
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
        Return a :py:class:`TaggedTextRegionMarkup` object for displaying text with region tags highlighted

        - highlight: List of region tag classes to highlight
        """
        if len(highlight) == 0:
            highlight = DEFAULT_HIGHLIGHT_REGIONS
        return TaggedTextRegionMarkup(self, highlight)

    def table(self, highlight=DEFAULT_HIGHLIGHT_REGIONS, display="html"):
        """
        Return a :py:class:`TaggedTextRegionTable` object for displaying region tags in tables

        - highlight: List of region tag classes to highlight
        - display: The type of HTML that will be generated. Either "html" or "csv-download"
        """
        if len(highlight) == 0:
            highlight = DEFAULT_HIGHLIGHT_REGIONS
        return TaggedTextRegionTable(self, highlight, display=display)


class TaggedTextRegionMarkup:
    """
    Represents a stream of starting/closing tags for all regions, which can be turned into e.g. HTML markup.

    - tt: The :py:class:`TaggedText` object to present
    - highlight: A list of region classes to highlight in the output, e.g. ``['quote.quote']``
    """

    def __init__(self, tt, highlight):
        self.tt = tt
        self.highlight = highlight

    def iter(self):
        """
        Returns an iterator of `Insert` objects, which correspond to the position of HTML tags,
        in order of position in text.

        An `Insert` object is a namedtuple of:

        - pos: Integer character position in text
        - opening: Boolean, an opening tag or closing tag?
        - rclass: Region class this relates to, e.g. ``quote.quote``
        - rvalue: Integer value associated with this rclass, e.g. chapter number
        """
        Insert = collections.namedtuple(
            "Insert", "pos region_start opening rclass rvalue"
        )
        # Generate opening/closing inserts for each region we are interested in
        inserts = []
        for rclass in self.tt.regions.keys():
            if rclass == "tokens" and "tokens" not in self.highlight:
                continue
            for r in self.tt.regions[rclass]:
                inserts.append(
                    Insert(
                        pos=r[0],
                        region_start=r[0],
                        opening=True,
                        rclass=rclass,
                        rvalue=r[2] if len(r) > 2 else None,
                    )
                )
                inserts.append(
                    Insert(
                        pos=r[1],
                        region_start=r[0],
                        opening=False,
                        rclass=rclass,
                        rvalue=r[2] if len(r) > 2 else None,
                    )
                )
        # NB: We want to sort by pos, then region_start, so closes happen before opens
        inserts.sort()
        return iter(inserts)

    def _repr_html_(self):
        """Return concatenated HTML for IPython"""
        return "".join(self.gen_html())

    def __html__(self):
        """Return concatenated HTML for other modules"""
        # https://github.com/ipython/ipython/blob/master/IPython/core/display.py#L419
        return self._repr_html_()

    def gen_html(self):
        """
        Returns an iterator that gives :py:class:`TaggedText` content as HTML markup.
        """
        return _gen_markup_html(self)

    def gen_ansi(self):
        """
        Returns an iterator that gives :py:class:`TaggedText` content with regions marked up with ANSI color codes.
        """
        return _gen_markup_ansi(self)


class TaggedTextRegionTable:
    def __init__(self, tt, highlight, display="html"):
        self.tt = tt
        self.highlight = highlight
        if display not in set(("html", "csv-download")):
            raise ValueError("Unknown display type %s" % display)
        self.display = display

    def iter(self):
        """
        Returns an iterator of `Region` objects, which correspond to all selected region classes.

        A `Region` object is a namedtuple of:

        - rclass: Region class this relates to, e.g. ``quote.quote``
        - pos_start: Integer character starting position in text
        - pos_end: Integer character ending position in text
        - rvalue: Integer value associated with this rclass, e.g. chapter number
        """
        Region = collections.namedtuple("Region", "rclass pos_start pos_end rvalue")

        # TODO: Markup does all of them here, we don't. Why?
        for i, rclass in enumerate(self.highlight):
            for r in self.tt.regions.get(rclass, []):
                yield Region(
                    rclass=rclass,
                    pos_start=r[0],
                    pos_end=r[1],
                    rvalue=(r[2] if len(r) > 2 else None),
                )

    def _repr_html_(self):
        """Return concatenated HTML for IPython"""
        if self.display == "html":
            return "".join(self.gen_html())
        elif self.display == "csv-download":
            return '<a download="%s" href="data:text/csv;base64,%s" target="_blank">Download %s</a>' % (
                (self.tt.name or "regions") + ".csv",
                base64.b64encode("".join(self.gen_csv()).encode("utf8")).decode(
                    "ascii"
                ),
                (self.tt.name or "regions") + ".csv",
            )
        else:
            raise ValueError(
                "Unknown display type %s, expected 'csv-download' or 'html'" % display
            )

    def __html__(self):
        """Return concatenated HTML for other modules"""
        # https://github.com/ipython/ipython/blob/master/IPython/core/display.py#L419
        return self._repr_html_()

    def gen_html(self):
        """
        Returns an iterator that gives :py:class:`TaggedText` content as an HTML table.
        """
        return _gen_table_html(self)

    def gen_csv(self):
        """
        Returns an iterator that gives :py:class:`TaggedText` content as lines of a CSV file.
        """
        return _gen_table_csv(self)
