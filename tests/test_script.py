import subprocess
import unittest
import re
import tempfile
import time
import urllib.request


def run_script(content, args=[], regions=[]):
    process = subprocess.Popen(
        ["./bin/clictagger"] + args + ["-"] + regions,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = process.communicate(content.encode("utf8"))
    return out.decode("utf8")


class TestScript(unittest.TestCase):
    maxDiff = None

    def test_ansi(self):
        def tidy(s):
            # Remove legend
            s = re.sub(r"^.+-{71}\n", "", s, flags=re.MULTILINE + re.DOTALL)
            # Turn ESC into hash
            s = s.replace("\x1b", "#")
            return s

        # Strings get coloured
        self.assertEqual(
            tidy(run_script("'Hello there, 'I said.\n")),
            """
#[0;37;41m'Hello there, 'I said.#[0m
        """.strip(),
        )

        # We reset / set colours on newlines
        self.assertEqual(
            tidy(
                run_script(
                    "'Hello there,\nthis new line is still part of the quote,' I said.\n"
                )
            ),
            """
#[0;37;45m'Hello there,
#[0;37;45mthis new line is still part of the quote,'#[0;37;41m #[0;37;46mI said.#[0m
        """.strip(),
        )

        # Only colour with quote.quote
        self.assertEqual(
            tidy(
                run_script(
                    "'Hello there,\nthis new line is still part of the quote,' I said.\n",
                    regions=["quote.quote"],
                )
            ),
            """
#[0;37;44m'Hello there,
#[0;37;44mthis new line is still part of the quote,'#[0m #[0mI said.#[0m
        """.strip(),
        )

    def test_csv(self):
        self.assertEqual(
            run_script(
                "'Hello there,\nthis new line is still part of the quote,' I said.\n",
                args=["--csv", "-"],
            ),
            """
"Region class","Start","End","Region value","Content"\r
chapter.sentence,0,64,"1","'Hello there, this new line is still part of the quote,' I said."\r
quote.quote,0,56,"","'Hello there, this new line is still part of the quote,'"\r
quote.suspension.short,57,64,"","I said."
        """.strip()
            + "\r\n",
        )

        self.assertEqual(
            run_script(
                "'Hello there,\nthis new line is still part of the quote,' I said.\n",
                args=["--csv", "-"],
                regions=["quote.quote"],
            ),
            """
"Region class","Start","End","Region value","Content"\r
quote.quote,0,56,"","'Hello there, this new line is still part of the quote,'"\r
        """.strip()
            + "\r\n",
        )

    def test_html(self):
        # Test we at least get output, the HTML is long and convoluted
        self.assertIn(
            "Hello there",
            run_script(
                "'Hello there,\nthis new line is still part of the quote,' I said.\n",
                args=["--html", "-"],
            ),
        )

    def test_serve(self):
        with tempfile.NamedTemporaryFile() as f:
            f.write("'Hello there,' I said.'\n".encode("utf8"))
            f.flush()

            process = subprocess.Popen(
                ["./bin/clictagger", "--serve", f.name],
            )
            try:
                time.sleep(1)
                with urllib.request.urlopen("http://localhost:8080") as out:
                    self.assertIn("Hello there,", out.read().decode("utf8"))
            finally:
                process.kill()
