"""
clictagger.taggedtext: Region-tag text
**************************************

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

    >>> print("".join(tt.table().gen_csv()))
    "Region class","Start","End","Region value","Content"
    metadata.title,0,28,"","The Dove in the Eagle's Nest"
    metadata.author,29,47,"","Charlotte M. Yonge"
    chapter.sentence,49,77,"1","“Thou find’st it out, child?"
    chapter.sentence,79,151,"2","Ay, ’tis worth all the feather-beds and pouncet-boxes in Ulm; is it not?"
    chapter.sentence,153,215,"3","That accursed Italian fever never left me till I came up here."
    chapter.sentence,217,280,"4","A man can scarce draw breath in your foggy meadows below there."
    chapter.sentence,282,316,"5","Now then, ‘here is the view open.’"
    chapter.sentence,318,354,"6","What think you of the Eagle’s Nest?”"
    quote.quote,49,354,"","“Thou find’st it out, child?  Ay, ’tis worth all the feather-beds and pouncet-boxes in Ulm; is it not?  That accursed Italian fever never left me till I came up here.  A man can scarce draw breath in your foggy meadows below there.  Now then, ‘here is the view open.’  What think you of the Eagle’s Nest?”"
    <BLANKLINE>
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
    def __init__(self, content, name=None):
        """"""
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
        if text_path == "-":
            return cls(sys.stdin.read(), name="stdin")
        with open(text_path, "r") as f:
            return cls(f.read(), name=text_path)

    @classmethod
    def from_github(cls, file_path, repo="birmingham-ccr/corpora", tag="master"):
        """e.g. TaggedText.from_github("ChiLit/alice.txt", tag = "80d00e4")"""
        if repo == "birmingham-ccr/corpora" and not file_path.endswith(".txt"):
            file_path += ".txt"
        return cls.from_url(
            "/".join(("https://raw.githubusercontent.com", repo, tag, file_path))
        )

    @classmethod
    def from_url(cls, url):
        """e.g. TaggedText.from_url("http://www.gutenberg.org/files/36/36-0.txt")"""
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
        return list(self.regions.keys())

    def markup(self, highlight=DEFAULT_HIGHLIGHT_REGIONS):
        if len(highlight) == 0:
            highlight = DEFAULT_HIGHLIGHT_REGIONS
        return TaggedTextRegionMarkup(self, highlight)

    def table(self, highlight=DEFAULT_HIGHLIGHT_REGIONS, display="html"):
        if len(highlight) == 0:
            highlight = DEFAULT_HIGHLIGHT_REGIONS
        return TaggedTextRegionTable(self, highlight, display=display)
