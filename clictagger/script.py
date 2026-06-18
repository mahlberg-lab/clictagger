"""
clictagger.script: Command line interface
*****************************************

Once clictagger is installed, you will have a command-line interface ``clictagger`` available.

Basic examples
--------------

To see the contents of ``alice.txt`` with :py:data:`default region tags <clictagger.taggedtext.DEFAULT_HIGHLIGHT_REGIONS>` coloured::

    clictagger alice.txt

To see the contents of ``alice.txt`` with quotes coloured::

    clictagger alice.txt quote.quote

Output all suspensions in ``alice.txt`` into ``alice.csv``::

    clictagger --csv alice.csv alice.txt --region quote.suspension.short quote.suspension.long

Output :py:data:`default region tags <clictagger.taggedtext.DEFAULT_HIGHLIGHT_REGIONS>` in ``alice.txt`` into ``alice.csv``::

    clictagger --csv alice.csv alice.txt

On Windows, to tag all text files in the current directory at once::

    for %f in (*.txt) do (clictagger --csv %f.csv %f)

On MacOs, to tag all text files in the current directory at once::

    for f in *.txt ; do clictagger --csv $f.csv $f; done

If the previous step does not work for you on Linux, to tag all text files in the current directory at once, try the following::

    for f in *.txt ; do ./bin/clictagger --csv $f.csv $f; done

Using clictagger as a webserver for cleaning text
-------------------------------------------------

For optimal use with clictagger, text needs to be cleaned up first.
For instance, text downloaded from the Gutenberg project will have large sections of non-authorial text.
See :ref:`Preparing texts for CLiCTagger` for how best to prepare text.

clictagger can be used to assist this process by creating a preview of the tagged regions with the following steps, given a text file ``new.txt``:

1. Open ``new.txt`` in a text-editor, e.g. Notepad.
2. In a terminal window, run ``clictagger --serve new.txt``
3. If a web-browser window hasn't automatically opened, open http://localhost:8080/ in your web browser.

Now you can make edits to ``new.txt``, reload your browser window, and changes will be visible.
"""

import argparse
import http.server
import itertools
import re
import subprocess
import shutil
import sys
import webbrowser

from .taggedtext import TaggedText


def _full_html(files, regions):
    def to_anchor(f):
        return re.sub(r"\W", "-", f)

    if len(files) > 1:
        yield '<h2><a name="contents">Contents</a></h2><ul>'
        for f in files:
            yield '<li><a href="#%s">%s</a></li>' % (to_anchor(f), f)
        yield "</ul><hr>"

    yield """<!DOCTYPE html>
    <html><head><meta charset="utf-8" /><style>
      body { font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans","Liberation Sans",sans-serif,"Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Noto Color Emoji"; }
      .legend {
        position: fixed;
        top: 2rem; right: 2rem;
        padding: 1rem 2rem;
        list-style: none;
        border: 1px solid #333;
        border-radius: 3px;
        background: #EEE;
      }
      .clictagger-tt ~ .clictagger-tt > .legend { display: none }
    </style></head><body>
    """
    for f in files:
        if len(files) > 1 and f != "-":
            yield '<h2><a name="%s">%s</a> <small>(<a href="#contents">up</a>)</small></h2>' % (
                to_anchor(f),
                f,
            )
        yield from TaggedText.from_file(f).markup(highlight=regions).gen_html()
        if len(files) > 1:
            yield "<hr>"
    yield "</body></html>\n"


def _serve_method(fn):
    """Start a server that serves the single-page result. fn is a function that returns an iterator"""

    class RequestHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                for x in fn():
                    self.wfile.write(x.encode("utf8"))
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write("NOT FOUND".encode("utf8"))

    server_address = ("0.0.0.0", 8080)
    httpd = http.server.HTTPServer(server_address, RequestHandler)
    print("Starting webserver. Press Ctrl-C to stop.")
    print(
        "Visit http://localhost:%d/ in your webbrowser to view output"
        % server_address[1]
    )
    try:
        webbrowser.open("http://localhost:%d/" % server_address[1])
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        pass


def clictagger():
    """:meta private: Entry point for command line interface"""
    ap = argparse.ArgumentParser()
    ap_mode = ap.add_mutually_exclusive_group()
    ap_mode.add_argument(
        "--ansi",
        help="Output text with regions colored with ANSI codes (for viewing in terminal)",
        action="store_true",
    )
    ap_mode.add_argument(
        "--csv",
        type=str,
        help="Output CSV to file (or '-' STDOUT)",
    )
    ap_mode.add_argument(
        "--html",
        type=str,
        help="Output HTML to file (or '-' STDOUT)",
    )
    ap_mode.add_argument(
        "--serve",
        help="Start a webserver to view output",
        action="store_true",
    )
    ap.add_argument(
        "--region",
        type=str,
        nargs="*",
        default=[],
        help="Region names to highlight. Defaults to sentences and quotes",
    )
    ap.add_argument(
        "input",
        type=str,
        nargs="*",
        default=["-"],
        help="File containing input text, or '-' for STDIN. Defaults to STDIN",
    )
    args = ap.parse_args()

    if args.serve:

        def serve_iter():
            yield from _full_html(args.input, args.region)

        _serve_method(serve_iter)
        exit(0)

    if args.input == "-" and sys.stdin.isatty():
        print(
            "You have selected to tag STDIN without piping another command into clictagger, this is probably a mistake."
        )
        print("To use STDIN input, use a pipe. For example:")
        print("    curl http://.../alice.txt | clictagger")
        print("For more help:")
        print("    clictagger --help")
        exit(1)

    if args.csv is not None:
        out_iter = itertools.chain(
            *(
                TaggedText.from_file(f).table(highlight=args.region).gen_csv()
                for f in args.input
            )
        )
        out_path = args.csv
    elif args.html is not None:
        out_iter = _full_html(args.input, args.region)
        out_path = args.html
    else:  # Assume ansi if nothing else given
        out_iter = itertools.chain(
            *(
                TaggedText.from_file(f).markup(highlight=args.region).gen_ansi()
                for i, f in enumerate(args.input)
            )
        )
        out_path = "-"

    pager = None
    less_path = shutil.which("less")
    if (
        out_path == "-" and less_path is not None and sys.stdout.isatty()
    ):  # Wrap direct TTY output with a pager
        pager = subprocess.Popen(
            [less_path, "-RSFi"], stdin=subprocess.PIPE, encoding="utf8"
        )
        out_f = pager.stdin
    elif out_path == "-":
        out_f = sys.stdout
    else:
        out_f = open(out_path, "w", newline="", encoding="utf8")

    try:
        for h in out_iter:
            out_f.write(h)
    except BrokenPipeError:
        # Pager lost interest
        pass

    if pager is not None:
        pager.communicate("")
    out_f.close()
