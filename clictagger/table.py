import html


def _gen_table_html(ttrt):
    yield "<table>\n"
    yield "<tr><th>Region class</th><th>Start</th><th>End</th><th>Region value</th><th>Content</th></tr>\n"
    for r in ttrt.iter():
        yield '<tr><td>%s</td> <td>%d</td> <td>%d</td> <td>%s</td> <td style="text-align: left">%s</td></tr>\n' % (
            r.rclass,
            r.pos_start,
            r.pos_end,
            html.escape(str(r.rvalue or "")),
            html.escape(ttrt.tt.content[r.pos_start : r.pos_end]),
        )
    yield "</table>\n"


def _gen_table_csv(ttrt):
    def escape_cell(s):
        # NB: Newline mangling from clic/client/lib/filesystem.js
        return s.replace('"', '""').replace("\n\n", "¶ ").replace("\n", " ")

    yield '"Region class","Start","End","Region value","Content"\r\n'
    for r in ttrt.iter():
        yield '%s,%d,%d,"%s","%s"\r\n' % (
            r.rclass,
            r.pos_start,
            r.pos_end,
            escape_cell(str(r.rvalue or "")),
            escape_cell(ttrt.tt.content[r.pos_start : r.pos_end]),
        )
