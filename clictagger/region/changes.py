"""
clictagger.region.changes: Regions that have changed since a previous revision
******************************************************************************

Uses :mod:`difflib` from the standard library to identify changes between a
previous revision of the content and the current version.

:func:`tagger_changes` adds:

- ``changes.changed``: Character ranges in the current content that are
  inserted or altered relative to the previous revision.

    >>> from functools import partial

No changes between revisions
----------------------------

If the previous revision is identical to the current content, no
``changes.changed`` ranges are produced::

    >>> previous = '''
    ... First paragraph.
    ...
    ... Second paragraph.
    ... '''.strip()
    >>> current = previous
    >>> [x for x in run_tagger(current,
    ...     partial(tagger_changes, content=current, previous_content=previous))
    ...  if x[0].startswith('changes.')]
    []

Character-level edit within a paragraph
---------------------------------------

A single-character substitution is narrowed down to just the changed
character(s)::

    >>> previous = '''
    ... First paragraph.
    ...
    ... Second paragraph.
    ...
    ... Third paragraph.
    ... '''.strip()
    >>> current = '''
    ... First paragraph.
    ...
    ... Second paragraph!
    ...
    ... Third paragraph.
    ... '''.strip()
    >>> [x for x in run_tagger(current,
    ...     partial(tagger_changes, content=current, previous_content=previous))
    ...  if x[0].startswith('changes.')]
    [('changes.changed', 34, 35, None, '!')]

Text appended to an existing paragraph
--------------------------------------

Only the appended run of characters is flagged as changed::

    >>> previous = '''
    ... First paragraph.
    ...
    ... Second paragraph.
    ... '''.strip()
    >>> current = '''
    ... First paragraph.
    ...
    ... Second paragraph, with extra words.
    ... '''.strip()
    >>> [x for x in run_tagger(current,
    ...     partial(tagger_changes, content=current, previous_content=previous))
    ...  if x[0].startswith('changes.')]
    [('changes.changed', 34, 52, None, ', with extra words')]

Inserted paragraph
------------------

Inserting a new paragraph between existing ones flags the inserted range,
including the trailing blank line separator::

    >>> previous = '''
    ... First paragraph.
    ...
    ... Third paragraph.
    ... '''.strip()
    >>> current = '''
    ... First paragraph.
    ...
    ... Brand new paragraph.
    ...
    ... Third paragraph.
    ... '''.strip()
    >>> [x for x in run_tagger(current,
    ...     partial(tagger_changes, content=current, previous_content=previous))
    ...  if x[0].startswith('changes.')]
    [('changes.changed', 18, 40, None, 'Brand new paragraph.\\n\\n')]
"""

import difflib
import os.path
import subprocess


def _line_offsets(lines):
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    return offsets


def _iter_added_ranges(old_text, new_text):
    """Yield ``(start, end)`` character ranges in ``new_text`` for content
    that is inserted or replaced relative to ``old_text``.

    Diffs at line granularity first, then refines each changed run at
    character granularity so end-of-line substitutions don't highlight
    whole lines.

    Line insertion:

    >>> list(_iter_added_ranges("a\\nb\\n", "a\\nNEW\\nb\\n"))
    [(2, 6)]

    Character substitution within a line:

    >>> list(_iter_added_ranges("Rudge\\n", "Rudgey\\n"))
    [(5, 6)]

    Unchanged:

    >>> list(_iter_added_ranges("same\\n", "same\\n"))
    []
    """
    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)
    new_offsets = _line_offsets(new_lines)

    line_matcher = difflib.SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
    for tag, i1, i2, j1, j2 in line_matcher.get_opcodes():
        if tag == "equal" or tag == "delete":
            continue
        if tag == "insert":
            yield (new_offsets[j1], new_offsets[j2])
            continue
        # 'replace': refine at character level within the changed run.
        old_chunk = "".join(old_lines[i1:i2])
        new_chunk = "".join(new_lines[j1:j2])
        base = new_offsets[j1]
        char_matcher = difflib.SequenceMatcher(a=old_chunk, b=new_chunk, autojunk=False)
        for ctag, _, _, cj1, cj2 in char_matcher.get_opcodes():
            if ctag in ("insert", "replace"):
                yield (base + cj1, base + cj2)


def tagger_changes(regions, content, previous_content):
    regions["changes.changed"] = list(_iter_added_ranges(previous_content, content))


def git_oldrev(file_path, git_ref, git_exec="git"):
    """Return the contents of ``file_path`` as it was at ``git_ref``.

    Runs ``git show <git_ref>:./<file>`` from the directory containing
    ``file_path``, so the lookup respects the enclosing repository and any
    relative path components. Intended as the ``previous_content`` argument to
    :func:`tagger_changes` when comparing a working-tree file against an
    earlier revision.

    - file_path: Path to the file on disk. Its directory selects the
      repository (via ``git -C``) and its basename selects the file to show.
    - git_ref: Any ref ``git show`` accepts, e.g. a branch name, tag, or SHA.
    - git_exec: Path to the ``git`` executable; override for testing or
      non-default installs.
    """
    cmd = [
        git_exec,
        "-C",
        str(os.path.dirname(file_path) or "."),
        "show",
        "{}:./{}".format(git_ref, os.path.basename(file_path)),
    ]
    return subprocess.check_output(cmd, encoding="utf-8")
