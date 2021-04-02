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


class TaggedTextRegionMarkup:
    def __init__(self, tt, highlight):
        self.tt = tt
        self.highlight = highlight

    def iter(self):
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
        return inserts

    def gen_html(self):
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
        tt_id = "tt-%s" % "".join(
            random.choice(string.ascii_lowercase) for i in range(20)
        )

        # Generate CSS
        css = "<style>%s</style>" % html.escape(HTML_CSS.replace("#tt-ID", "#" + tt_id))
        for i, rclass in enumerate(self.highlight):
            css = css.replace(".highlight-%d" % i, "." + rclass_css(rclass))
        yield css

        start = 0
        open_regions = {}
        yield '<div class="clictagger-tt" id="%s">' % tt_id
        yield '<ul class="legend">'
        for rclass in self.highlight:
            yield '<li class="%s">%s</li>' % (
                rclass_css(rclass),
                html.escape(rclass),
            )
        yield "</ul>"
        yield "<span>"
        for insert in self.iter():
            if insert.pos > start:
                # If text is available, start a span with correct regions and insert it
                yield '</span><span title="%s" class="%s">' % (
                    " ".join(region_title(r) for r in open_regions.values()),
                    " ".join(rclass_css(r.rclass) for r in open_regions.values()),
                )
                yield text_to_html(self.tt.content[start : insert.pos])
                start = insert.pos
            if insert.opening:
                open_regions[insert.rclass] = insert
            else:
                del open_regions[insert.rclass]
        yield "</span></div>"

    def _repr_html_(self):
        """Return concatenated HTML for IPython"""
        return "".join(self.gen_html())
        # TODO: Output isn't saving well, possibly not well-formed?

    def __html__(self):
        """Return concatenated HTML for other modules"""
        # https://github.com/ipython/ipython/blob/master/IPython/core/display.py#L419
        return self._repr_html_()

    def gen_ansi(self):
        """Based on algorithm in client/lib/corpora_utils"""
        # Anything we aren't highlighting is mapped to 0, to reset colours
        colour_map = collections.defaultdict(lambda: 0)
        # Generate a legend
        yield "Legend:-\n"
        for i, rclass in enumerate(self.highlight):
            colour_map[rclass] = min(i + 1, len(REGION_COLOURS) - 1)
            yield "    %s%s%s\n" % (
                REGION_COLOURS[colour_map[rclass]],
                rclass,
                REGION_COLOURS[0],
            )
        yield "-----------------------------------------------------------------------\n"

        start = 0
        open_regions = {}
        for insert in self.iter():
            if rclass not in self.highlight:
                continue
            if insert.pos > start:
                for i, part in enumerate(
                    self.tt.content[start : insert.pos].split("\n")
                ):
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
