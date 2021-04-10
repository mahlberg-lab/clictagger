"""
clictagger.script: Command line interface
*****************************************

Once clictagger is installed, you will have a command-line interface ``clictagger`` available.

Basic examples
--------------

To see the contents of ``alice.txt`` with default regions coloured::

    clictagger alice.txt

To see the contents of ``alice.txt`` with quotes coloured::

    clictagger alice.txt quote.quote

Output all suspensions in ``alice.txt`` into ``alice.csv``::

    clictagger --csv alice.csv alice.txt quote.suspension.short quote.suspension.long

Using clictagger as a webserver for cleaning text
-------------------------------------------------

For optimal use with clictagger, text needs to be cleaned up first.
For instance, text downloaded from the Gutenberg project will have large sections of non-authorial text.
The standard process `is outlined here <https://github.com/birmingham-ccr/corpora#cleaning-of-corpora-texts>`.

clictagger can be used to assist this process with the following steps, given a text file ``new.txt``:

1. Open ``new.txt`` in a text-editor, e.g. Notepad.
2. In a terminal window, run ``clictagger --serve new.txt``
3. If a web-browser window hasn't automatically opened, open http://localhost:8080/ in your web browser.

Now you can make edits to ``new.txt``, reload your browser window, and changes will be visible.
"""
import argparse
import http.server
import subprocess
import shutil
import sys
import webbrowser

from .taggedtext import TaggedText


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
        "input",
        type=str,
        nargs="?",
        default="-",
        help="File containing input text, or '-' for STDIN. Defaults to STDIN",
    )
    ap.add_argument(
        "region",
        type=str,
        nargs="*",
        help="Region names to highlight. Defaults to sentences and quotes",
    )
    args = ap.parse_args()

    if args.serve:

        def serve_iter():
            yield "<!DOCTYPE html>\n<html><head></head><body>\n"

            # NB: Re-parse file on every request
            for h in (
                TaggedText.from_file(args.input)
                .markup(highlight=args.region)
                .gen_html()
            ):
                yield h

            yield "</body></html>\n"

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
        out_iter = (
            TaggedText.from_file(args.input).table(highlight=args.region).gen_csv()
        )
        out_path = args.csv
    elif args.html is not None:
        out_iter = (
            TaggedText.from_file(args.input).markup(highlight=args.region).gen_html()
        )
        out_path = args.html
    else:  # Assume ansi if nothing else given
        out_iter = (
            TaggedText.from_file(args.input).markup(highlight=args.region).gen_ansi()
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
