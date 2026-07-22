#!/usr/bin/env python3
"""Fail if the app references a CSS class that is never styled.

Written after a slice-replace that was meant to swap the panel action-bar CSS
silently deleted the field guide, lessons and list-view styles as well -- they
had been inserted into the same range, and nothing complained because unstyled
HTML still renders, just wrongly. A screenshot of one panel did not catch it.

Run before shipping a build.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
KNOWN_UNSTYLED = {"mod-solo", "mode-fun"}   # pre-existing, styled via other selectors


def main():
    h = (ROOT / "sap-table-explorer.html").read_text()
    style = h[h.index("<style>"):h.index("</style>")]
    body = h[h.index("</style>"):]
    used = set()
    for attr in re.findall(r'class="([^"$]+)"', body):
        for c in attr.split():
            if c and "${" not in c:
                used.add(c)
    defined = set(re.findall(r"\.([a-zA-Z][\w-]*)\s*[,{:]", style))
    missing = sorted(used - defined - KNOWN_UNSTYLED)
    if missing:
        print("UNSTYLED CLASSES — did a slice edit eat a CSS block?")
        for m in missing:
            print("  ." + m)
        sys.exit(1)
    print(f"styles ok — {len(used)} classes used, all defined")


if __name__ == "__main__":
    main()
