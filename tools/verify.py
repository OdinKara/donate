"""
verify.py - independently prove the COMMITTED artifacts are correct.

This does not trust make_qr.py. It reads the .svg files that are actually in the
repo, rasterises them itself, and decodes them with OpenCV - a completely
different code path from the one that wrote them. Then it checks the decoded
string against the address text in index.html.

Run from the repo root:  python tools/verify.py
Exit code 0 = every QR decodes to exactly the address printed beside it.
"""

import pathlib
import re
import sys

import numpy as np
import cv2

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXPECTED = {
    "bitcoin": "bc1q9c2jx7ve0s2g7pg4fp3wkg7sqyk0zueyqj9jp5",
    "lightning": "wwbd@strike.me",
}


def svg_to_array(path: pathlib.Path, scale: int = 8) -> np.ndarray:
    """Rasterise an SvgPathImage QR: one <path> of 'M x y h N v N h -N z' rects."""
    text = path.read_text(encoding="utf-8")
    m = re.search(r'viewBox="0 0 (\d+(?:\.\d+)?) (\d+(?:\.\d+)?)"', text)
    if not m:
        raise SystemExit(f"{path.name}: no viewBox")
    w, h = int(float(m.group(1))), int(float(m.group(2)))
    canvas = np.full((h * scale, w * scale), 255, dtype=np.uint8)

    d = re.search(r'\sd="([^"]+)"', text)
    if not d:
        raise SystemExit(f"{path.name}: no path data")
    # Each dark module is one absolute subpath: M<x>,<y>H<x2>V<y2>H<x>z
    for mx, my, mx2, my2 in re.findall(
        r"M(\d+),(\d+)H(\d+)V(\d+)", d.group(1)
    ):
        x, y, x2, y2 = int(mx), int(my), int(mx2), int(my2)
        canvas[y * scale : y2 * scale, x * scale : x2 * scale] = 0

    # Pad with white. The SVG carries a 4-module quiet zone already, but extra
    # slack costs nothing and keeps the detector off the image edge.
    return cv2.copyMakeBorder(canvas, 40, 40, 40, 40, cv2.BORDER_CONSTANT, value=255)


def main() -> int:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    failures = []

    for name, expected in EXPECTED.items():
        svg = ROOT / "qr" / f"{name}.svg"
        if not svg.exists():
            failures.append(f"{name}: {svg} missing")
            continue

        decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(svg_to_array(svg))
        if decoded != expected:
            failures.append(f"{name}: QR decodes to {decoded!r}, expected {expected!r}")
        else:
            print(f"[OK] qr/{name}.svg decodes to {decoded}")

        if expected not in html:
            failures.append(f"{name}: {expected!r} does not appear in index.html")
        else:
            print(f"[OK] index.html shows {expected}")

    # The page must make zero external requests. Anything that fetches a
    # subresource from another origin is an address-swap vector.
    for bad in re.findall(r'(?:src|href)\s*=\s*"(https?://[^"]+)"', html):
        # Plain outbound <a> links are the point of the page; only subresource
        # loads matter. Flag anything that is not an anchor target.
        idx = html.find(bad)
        tag_start = html.rfind("<", 0, idx)
        if not html[tag_start : tag_start + 2].lower() == "<a":
            failures.append(f"external subresource: {bad}")

    for f in failures:
        print(f"[X] {f}")
    if failures:
        return 1
    print("\n[OK] all QR images and page addresses agree.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
