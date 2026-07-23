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

#tt-ID .legend button:first-child {
  float: left;
  margin-right: 0.5rem;
}

#tt-ID .legend button:last-child {
  float: right;
  margin-left: 0.5rem;
}

@keyframes tt-blink {
  from { outline: 3px solid orangered; }
  to { outline: 3px solid transparent; }
}

#tt-ID .tt-blink {
  animation: tt-blink 1.5s ease-out;
}

#tt-ID .highlight-chapter-sentence {
    border-top: 1px solid #555;
    border-bottom: 1px solid #555;
    background: #eee;
}

#tt-ID .highlight-chapter-sentence:first-child {
    border-inline-start: 1px solid #555;
}

#tt-ID :not(.highlight-chapter-sentence) + .highlight-chapter-sentence {
    border-inline-start: 1px solid #555;
}

#tt-ID .highlight-chapter-sentence:not(:has(+ .highlight-chapter-sentence)) {
    border-inline-end: 1px solid #555;
}

#tt-ID .highlight-changes-changed {
   text-decoration-style: wavy;
   text-decoration-line: underline;
   text-decoration-color: darkgreen;
}

#tt-ID .highlight-0 { background: cornflowerblue }
#tt-ID .highlight-1 { background: yellowgreen }
#tt-ID .highlight-2 { background: palevioletred }
#tt-ID .highlight-3 { background: violet }
#tt-ID .highlight-4 { background: skyblue }
#tt-ID .highlight-5 { background: goldenrod }
""".strip()

HTML_JS = """
function selectMatch(newMatches) {
  (window.lastMatches || []).forEach(function (el) {
    // Remove any previous blink and force reflow (in case we're the only element)
    el.classList.remove("tt-blink");
    void el.offsetWidth;
  });
  window.lastMatches = newMatches;

  window.lastMatches[0].scrollIntoView({behaviour: "smooth", block: "center"});
  window.lastMatches.forEach(function (el) {
    el.classList.add("tt-blink");
  });
  window.setTimeout(function (elsPrev) {
    elsPrev.forEach(function (el) {
      el.classList.remove("tt-blink");
    });
  }, 1500, window.lastMatches);
}

document.querySelectorAll("ul.legend button[data-dir='right']").forEach(function (elButton) {
  elButton.onclick = function (event) {
    var searchForClass = event.target.parentElement.querySelector(":scope > span").className;
    var lastMatch = window.lastMatches ? window.lastMatches[window.lastMatches.length - 1] : null;
    let nextMatch;

    if (lastMatch) {
      for (let s = lastMatch.nextElementSibling; s && !nextMatch; s = s.nextElementSibling) {
        // Look for following matches in the same document
        if (s.matches("span." + searchForClass)) nextMatch = s;
      }
      if (!nextMatch) {
        const currentDoc = lastMatch.parentElement;
        for (let s = currentDoc.nextElementSibling; s && !nextMatch; s = s.nextElementSibling) {
          // Look for matches in following documents
          nextMatch = s.querySelector(":scope > span." + searchForClass);
        }
      }
    }
    if (!nextMatch) {
      // Look for matches everywhere
      nextMatch = window.document.querySelector("div.clictagger-tt > span." + searchForClass);
    }
    if (!nextMatch) {
      window.alert("There are no instances of " + searchForClass + " in the document");
      return;
    }

    // Collect subsequent spans with the same class
    nextMatch = [nextMatch];
    for (let s = nextMatch[nextMatch.length - 1].nextElementSibling; s; s = s.nextElementSibling) {
      if (s.matches("span." + searchForClass)) {
        nextMatch.push(s);
      } else {
        break;
      }
    }

    selectMatch(nextMatch);
  };
});

document.querySelectorAll("ul.legend button[data-dir='left']").forEach(function (elButton) {
  elButton.onclick = function (event) {
    var searchForClass = event.target.parentElement.querySelector(":scope > span").className;
    var lastMatch = window.lastMatches ? window.lastMatches[0] : null;
    let nextMatch;

    if (lastMatch) {
      for (let s = lastMatch.previousElementSibling; s && !nextMatch; s = s.previousElementSibling) {
        // Look for preceding matches in the same document
        if (s.matches("span." + searchForClass)) nextMatch = s;
      }
      if (!nextMatch) {
        const currentDoc = lastMatch.parentElement;
        for (let s = currentDoc.previousElementSibling; s && !nextMatch; s = s.previousElementSibling) {
          // Look for matches in preceding documents, take the last match in each
          const matches = s.querySelectorAll(":scope > span." + searchForClass);
          nextMatch = matches[matches.length - 1];
        }
      }
    }
    if (!nextMatch) {
      // Look for matches everywhere, take the last one
      const matches = window.document.querySelectorAll("div.clictagger-tt > span." + searchForClass);
      nextMatch = matches[matches.length - 1];
    }
    if (!nextMatch) {
      window.alert("There are no instances of " + searchForClass + " in the document");
      return;
    }

    // Collect previous spans with the same class
    nextMatch = [nextMatch];
    for (let s = nextMatch[0].previousElementSibling; s; s = s.previousElementSibling) {
      if (s.matches("span." + searchForClass)) {
        nextMatch.push(s);
      } else {
        break;
      }
    }
    nextMatch.reverse();

    selectMatch(nextMatch);
  };
});
""".strip()

RCLASS_CUSTOM_CSS_RULES = set(
    (
        "chapter.sentence",
        "changes.changed",
    )
)

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
        css = css.replace(
            ".highlight-%s" % rclass_css(rclass), "." + rclass_css(rclass)
        )
        # chapter.sentence has it's own custom highlight rules
        if rclass not in RCLASS_CUSTOM_CSS_RULES:
            css = css.replace(".highlight-%d" % i, "." + rclass_css(rclass))
    yield css

    start = 0
    open_regions = {}
    yield '<div class="clictagger-tt" id="%s">' % tt_id
    yield '<ul class="legend">'
    for rclass in ttrm.highlight:
        yield '<li><button data-dir="left">◄</button><span class="%s">%s</span><button data-dir="right">►</button></li>' % (
            rclass_css(rclass),
            html.escape(rclass),
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
            del open_regions[insert.rclass]
    yield "</span></div>"

    # Generate JS
    yield "<script>%s</script>" % HTML_JS


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
