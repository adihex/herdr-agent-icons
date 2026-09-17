# /// script
# requires-python = ">=3.9"
# dependencies = ["fonttools>=4.50"]
# ///
"""Build AgentIcons.ttf from logos/*.svg.

Each SVG becomes one glyph in the Unicode Private Use Area (U+E000+).
Outputs:
  build/AgentIcons.ttf   - install into ~/Library/Fonts (macOS)
  build/codepoints.tsv   - <logo-name>\t<char> used by report-once.sh

Run:  uv run tools/build-font.py
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.svgLib.path import parse_path

ROOT = Path(__file__).resolve().parent.parent
LOGOS = ROOT / "logos"
BUILD = ROOT / "build"
UPM = 1000

# --- minimal SVG -> path-d normalization -------------------------------------

def _num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default

def shape_to_d(el):
    tag = el.tag.rsplit("}", 1)[-1]
    a = el.attrib
    if tag == "rect":
        x, y = _num(a.get("x")), _num(a.get("y"))
        w, h = _num(a.get("width")), _num(a.get("height"))
        return f"M{x},{y}h{w}v{h}h{-w}Z"
    if tag == "circle":
        cx, cy, r = _num(a.get("cx")), _num(a.get("cy")), _num(a.get("r"))
        return (f"M{cx - r},{cy}a{r},{r} 0 1,0 {2*r},0a{r},{r} 0 1,0 {-2*r},0Z")
    if tag == "ellipse":
        cx, cy = _num(a.get("cx")), _num(a.get("cy"))
        rx, ry = _num(a.get("rx")), _num(a.get("ry"))
        return (f"M{cx - rx},{cy}a{rx},{ry} 0 1,0 {2*rx},0a{rx},{ry} 0 1,0 {-2*rx},0Z")
    if tag in ("polygon", "polyline"):
        pts = re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", a.get("points", ""))
        pairs = list(zip(pts[::2], pts[1::2]))
        if not pairs:
            return None
        d = f"M{pairs[0][0]},{pairs[0][1]}" + "".join(f"L{x},{y}" for x, y in pairs[1:])
        return d + ("Z" if tag == "polygon" else "")
    return a.get("d")

_TOK = re.compile(r"(matrix|translate|scale|rotate|skewX|skewY)\s*\(([^)]*)\)")

def parse_transform(s):
    t = Transform()
    for fn, args in _TOK.findall(s or ""):
        v = [float(x) for x in re.findall(r"-?\d*\.?\d+(?:e-?\d+)?", args)]
        if fn == "matrix" and len(v) == 6:
            t = t.transform(Transform(*v))
        elif fn == "translate":
            t = t.transform(Transform(1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0))
        elif fn == "scale":
            t = t.transform(Transform(v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0))
        elif fn == "rotate" and v:
            import math
            rad = math.radians(v[0])
            r = Transform(math.cos(rad), math.sin(rad), -math.sin(rad), math.cos(rad), 0, 0)
            if len(v) == 3:  # rotate about (cx, cy)
                cx, cy = v[1], v[2]
                r = Transform(1,0,0,1,cx,cy).transform(r).transform(Transform(1,0,0,1,-cx,-cy))
            t = t.transform(r)
    return t

def svg_to_glyph(svg_path):
    """Draw every shape in the SVG into one glyph, normalized to UPM box."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    vb = re.findall(r"-?\d*\.?\d+", root.attrib.get("viewBox", ""))
    if len(vb) == 4:
        vx, vy, vw, vh = map(float, vb)
    else:
        vx = vy = 0.0
        vw = _num(root.attrib.get("width"), UPM)
        vh = _num(root.attrib.get("height"), UPM)
    s = UPM / max(vw, vh)
    # x' = (x - vx)*s ; y' = (vh - (y - vy))*s
    base = Transform(s, 0, 0, -s, -vx * s, (vy + vh) * s)

    # Propagate ancestor transforms by walking the tree recursively.
    pen = T2CharStringPen(UPM, None)
    drawn = 0

    def walk(el, t):
        nonlocal drawn
        t = t.transform(parse_transform(el.attrib.get("transform")))
        if el.tag.rsplit("}", 1)[-1] in ("path", "rect", "circle", "ellipse", "polygon", "polyline"):
            d = shape_to_d(el)
            if d:
                try:
                    parse_path(d, TransformPen(pen, t))
                    drawn += 1
                except Exception as e:
                    print(f"  ! {svg_path.name}: skipped a path ({e})", file=sys.stderr)
        for child in el:
            walk(child, t)

    walk(root, base)
    return pen.getCharString(), drawn


def main():
    BUILD.mkdir(exist_ok=True)
    svgs = sorted(LOGOS.glob("*.svg"))
    if not svgs:
        sys.exit("no SVGs in logos/")

    empty = T2CharStringPen(UPM, None)
    names, glyphs, cps = [".notdef"], [empty.getCharString()], {}
    for i, svg in enumerate(svgs):
        g, n = svg_to_glyph(svg)
        name = svg.stem
        cp = 0x100000 + i  # Plane-16 PUA: Nerd Fonts occupy F0001..F1AF0.
        names.append(name)
        glyphs.append(g)
        cps[name] = cp
        print(f"{name:20s} U+{cp:04X}  ({n} path(s))")

    fb = FontBuilder(UPM, isTTF=False)
    fb.setupGlyphOrder(names)
    fb.setupCharacterMap({cp: name for name, cp in cps.items()})
    fb.setupCFF("AgentIcons-Regular",
                {"FullName": "AgentIcons Regular", "FamilyName": "AgentIcons"},
                dict(zip(names, glyphs)), {})
    fb.setupHorizontalMetrics({n: (UPM, 0) for n in names})
    fb.setupHorizontalHeader(ascent=UPM, descent=0)
    fb.setupNameTable({
        "familyName": "AgentIcons",
        "styleName": "Regular",
        "uniqueFontIdentifier": "AgentIcons Regular",
        "fullName": "AgentIcons Regular",
        "psName": "AgentIcons-Regular",
        "version": "Version 1.0",
    })
    fb.setupOS2(sTypoAscender=UPM, sTypoDescender=0, usWinAscent=UPM, usWinDescent=0)
    fb.setupPost()
    out = BUILD / "AgentIcons.otf"
    fb.save(out)

    with open(BUILD / "codepoints.tsv", "w") as f:
        for name, cp in cps.items():
            f.write(f"{name}\t{chr(cp)}\n")
    print(f"\nwrote {out} + build/codepoints.tsv")
    print("install: cp build/AgentIcons.otf ~/Library/Fonts/")

if __name__ == "__main__":
    main()
