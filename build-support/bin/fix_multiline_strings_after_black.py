# Copyright 2019 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

import sys
from typing import Iterator

# Fix multiline strings indentation after running black
#
# Note: This relies on the rest of the formatting having already been
# applied.
# This is an accepted limitation of this script. Simply run black first, then run
# this script to fix the multiline strings which have are inconsistently indented
# as a result of black's effort to leave the AST unchanged.
#
# Also note: Because we are simply monkey patching black, the same caching mechanism
# is applied, which means that no change will take effect if you run this script
# immediately after running black without clearing the cache in between.
# To clear the cache, run `rm -rf ~/Library/Caches/black` on MacOS
#
# This script will modify the content of your code: some strings will gain
# extra-spaces. For this reason, it shouldn't be part of Black itself as it
# would break the correctness property of Black.
#
# If you have a large codebase that used to be indented with two spaces and want to
# run black on it; and if you are willing to detect any regression this script
# introduces by manually fixing them, this script may help you to accomplish a
# more consistent looking codebase for the one-off cost of ensuring that any
# breakage is detected and fixed.
import black
from black import Line, is_multiline_string
from blib2to3.pytree import Leaf


def visit_string(self, leaf: Leaf) -> Iterator[Line]:
    if is_multiline_string(leaf):
        prefix = " " * leaf.column

        start_index = 3 + leaf.value.find('"""')
        if start_index == -1:
            # index/rindex: like find/rfind, but throw if not found
            start_index = 3 + leaf.value.index("'''")
            end_index = leaf.value.rindex("'''")
        else:
            end_index = leaf.value.rfind('"""')
        docstring = fix_multiline_string(leaf.value[start_index:end_index], prefix)
        leaf.value = leaf.value[0:start_index] + docstring + leaf.value[end_index:]

    visited = self.visit_default(leaf)
    yield from visited


def fix_multiline_string(multiline_string: str, prefix: str) -> str:
    # https://www.python.org/dev/peps/pep-0257/#handling-docstring-indentation
    if not multiline_string:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = multiline_string.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        last_line_idx = len(lines) - 2
        for i, line in enumerate(lines[1:]):
            stripped_line = line[indent:].rstrip()
            if stripped_line or i == last_line_idx:
                trimmed.append(prefix + stripped_line)
            else:
                trimmed.append("")
    # Consistently have a newline before the closing triple quote
    if trimmed[-1] != prefix:
        trimmed.append(prefix)
    # Return a single string:
    return "\n".join(trimmed)


black.LineGenerator.visit_STRING = visit_string
black.patched_main()
