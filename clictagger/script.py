import argparse
import http.server
import subprocess
import sys

from .taggedtext import TaggedText


def serve_method(fn):
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
    print("Starting server. Visit http://localhost:%d/" % server_address[1])
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        pass


def clictagger():
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

        serve_method(serve_iter)
        exit(0)

    if args.csv is not None:
        out_iter = (
            TaggedText.from_file(args.input).table(highlight=args.region).gen_csv()
        )
        out_path = args.csv
    elif args.html is not None:
        out_iter = (
            TaggedText.from_file(args.input).table(highlight=args.region).gen_html()
        )  # TODO: Should be markup
        out_path = args.html
    else:  # Assume ansi if nothing else given
        out_iter = (
            TaggedText.from_file(args.input).markup(highlight=args.region).gen_ansi()
        )
        out_path = "-"

    pager = None
    if out_path == "-" and sys.stdout.isatty():  # Wrap direct TTY output with a pager
        pager = subprocess.Popen(
            ["less", "-RSFi"], stdin=subprocess.PIPE, encoding="utf8"
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
