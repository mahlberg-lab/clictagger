import collections
import html
import random
import re
import string


HTML_CSS = """
#tt-ID {
  max-width: 960px;
  margin: auto;
  padding: 10px;
  line-height: 1.4em;
  font-family: serif;
  font-size: 1.1em;
}

#tt-ID .legend {
  float: right;
}

#tt-ID .highlight-chapter-sentence {
    border-top: 1px solid #555;
    border-bottom: 1px solid #555;
}

#tt-ID .highlight-chapter-sentence:first-child {
    border-inline-start: 1px solid #555;
}

#tt-ID :not(.highlight-chapter-sentence) + .highlight-chapter-sentence {
    border-inline-start: 1px solid #555;
}

#tt-ID .highlight-chapter-sentence-close {
    border-inline-end: 1px solid #555;
}

#tt-ID .highlight-0 { background: cornflowerblue }
#tt-ID .highlight-1 { background: yellowgreen }
#tt-ID .highlight-2 { background: palevioletred }
#tt-ID .highlight-3 { background: violet }
#tt-ID .highlight-4 { background: skyblue }
#tt-ID .highlight-5 { background: goldenrod }
""".strip()


REGION_COLOURS = [
    "\x1b[0m",
    "\x1b[0;37;44m",  # Blue
    "\x1b[0;37;42m",  # Green
    "\x1b[0;37;41m",  # Red
    "\x1b[0;37;45m",  # Magenta
    "\x1b[0;37;46m",  # Cyan
    "\x1b[0;37;43m",  # Yellow
]


def _gen_markup_html(ttrm):
    """Based on algorithm in client/lib/corpora_utils"""

    def text_to_html(s):
        """Reformat text into HTML"""
        # Turn initial spaces into &nbsp;s
        s = re.sub(
            r"\n +",
            lambda m: "&nbsp;" * (m.end() - m.start() - 1),
            s,
        )
        # Make new-lines <br/>
        s = s.replace("\n", "<br/>\n")
        return s

    def region_title(r):
        if r.rvalue is None:
            return r.rclass
        return r.rclass + ":" + str(r.rvalue)

    def rclass_css(rclass):
        return rclass.replace(".", "-")

    # Generate unique ID, to hang CSS off
    tt_id = "tt-%s" % "".join(random.choice(string.ascii_lowercase) for i in range(20))

    # Generate CSS
    css = "<style>%s</style>" % html.escape(HTML_CSS.replace("#tt-ID", "#" + tt_id))
    for i, rclass in enumerate(ttrm.highlight):
        css = css.replace(".highlight-%d" % i, "." + rclass_css(rclass))
        css = css.replace(
            ".highlight-%s" % rclass_css(rclass), "." + rclass_css(rclass)
        )
    yield css

    start = 0
    open_regions = {}
    yield '<div class="clictagger-tt" id="%s">' % tt_id
    yield '<ul class="legend">'
    for rclass in ttrm.highlight:
        yield '<li><span class="%s">%s</span><span class="%s"></span></li>' % (
            rclass_css(rclass),
            html.escape(rclass),
            rclass_css(rclass) + "-close",
        )
    yield "</ul>"
    yield "<span>"
    for insert in ttrm.iter():
        if insert.pos > start:
            # If text is available, start a span with correct regions and insert it
            yield '</span><span title="%s" class="%s">' % (
                " ".join(region_title(r) for r in open_regions.values()),
                " ".join(rclass_css(r.rclass) for r in open_regions.values()),
            )
            yield text_to_html(ttrm.tt.content[start : insert.pos])
            start = insert.pos
        if insert.opening:
            open_regions[insert.rclass] = insert
        else:
            if insert.rclass == "chapter.sentence":
                # NB: We need closing markers since CSS can't say "a sentence that is followed by non-sentence"
                yield '</span><span class="%s">' % (
                    rclass_css(insert.rclass) + "-close",
                )
            del open_regions[insert.rclass]
    yield "</span></div>"


def _gen_markup_ansi(ttrm):
    """Based on algorithm in client/lib/corpora_utils"""
    # Anything we aren't highlighting is mapped to 0, to reset colours
    colour_map = collections.defaultdict(lambda: 0)
    # Generate a legend
    yield "Legend:-\n"
    for i, rclass in enumerate(ttrm.highlight):
        colour_map[rclass] = min(i + 1, len(REGION_COLOURS) - 1)
        yield "    %s%s%s\n" % (
            REGION_COLOURS[colour_map[rclass]],
            rclass,
            REGION_COLOURS[0],
        )
    yield "-----------------------------------------------------------------------\n"

    start = 0
    open_regions = {}
    for insert in ttrm.iter():
        if rclass not in ttrm.highlight:
            continue
        if insert.pos > start:
            for i, part in enumerate(ttrm.tt.content[start : insert.pos].split("\n")):
                if i > 0:
                    yield "\n"
                # Set / reset region colours after every newline
                yield REGION_COLOURS[
                    max(
                        colour_map[rclass]
                        for rclass in open_regions.keys() or ["__reset"]
                    )
                ]
                yield part
            start = insert.pos
        if insert.opening:
            open_regions[insert.rclass] = True
        else:
            del open_regions[insert.rclass]
    yield REGION_COLOURS[colour_map["__reset"]]
