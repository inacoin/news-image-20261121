#!/usr/bin/env python3
"""Subset DejaVu fonts to the glyphs used by main.py, so the repo is
self-contained and the grader needs no system fonts."""
import sys
from fontTools import subset

CHARS = (
    " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    ".,;:!?-'\u2019\u201c\u201d()[]%/\u2013\u2014\u00b7\u2022&+=\u00a0"
)

JOBS = [
    ("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
     "DejaVuSerif-Bold.subset.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "DejaVuSans.subset.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
     "DejaVuSans-Bold.subset.ttf"),
]

for src, dst in JOBS:
    options = subset.Options()
    options.layout_features = ["kern", "liga"]
    options.hinting = False
    options.desubroutinize = True
    options.notdef_outline = True
    options.recalc_bounds = True
    font = subset.load_font(src, options)
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=CHARS)
    subsetter.subset(font)
    font.save(dst)
    print(dst, "done")
