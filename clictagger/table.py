import base64
import collections
import html


class TaggedTextRegionTable:
    def __init__(self, tt, highlight, display="html"):
        self.tt = tt
        self.highlight = highlight
        if display not in set(("html", "csv-download")):
            raise ValueError("Unknown display type %s" % display)
        self.display = display

    # TODO: Should self be the iterable here?
    def iter(self):
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

    def gen_html(self):
        yield "<table>\n"
        yield "<tr><th>Region class</th><th>Start</th><th>End</th><th>Region value</th><th>Content</th></tr>\n"
        for r in self.iter():
            yield '<tr><td>%s</td> <td>%d</td> <td>%d</td> <td>%s</td> <td style="text-align: left">%s</td></tr>\n' % (
                r.rclass,
                r.pos_start,
                r.pos_end,
                html.escape(str(r.rvalue or "")),
                html.escape(self.tt.content[r.pos_start : r.pos_end]),
            )
        yield "</table>\n"

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

    def gen_csv(self):
        def escape_cell(s):
            # NB: Newline mangling from clic/client/lib/filesystem.js
            return s.replace('"', '""').replace("\n\n", "¶ ").replace("\n", " ")

        yield '"Region class","Start","End","Region value","Content"\r\n'
        for r in self.iter():
            yield '%s,%d,%d,"%s","%s"\r\n' % (
                r.rclass,
                r.pos_start,
                r.pos_end,
                escape_cell(str(r.rvalue or "")),
                escape_cell(self.tt.content[r.pos_start : r.pos_end]),
            )
