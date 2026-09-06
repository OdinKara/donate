"""
make_qr.py - regenerate the committed QR images from the addresses in one place.

Run from the repo root:  python tools/make_qr.py

Deliberate choices:
  * SVG, not PNG. An SVG is text, so a QR swap shows up as a readable diff in
    git rather than as an opaque binary blob. That is the whole point of
    committing these images instead of calling a QR API at runtime.
  * Each QR encodes EXACTLY the string shown as selectable text next to it on
    the page - no bitcoin: URI wrapper, no amount, no label. What you scan and
    what you read are the same bytes, so the page can be audited by eye.
  * ERROR_CORRECT_M: enough redundancy for a phone camera, small enough to stay
    legible at 200px.
  * border=4: the quiet zone the QR spec requires. Anything smaller scans
    unreliably on real phone cameras.
"""

import pathlib
import qrcode
import qrcode.image.svg

# The single source of truth for this repo. index.html must match these byte
# for byte; verify.py checks that.
PAYLOADS = {
    "bitcoin": "bc1q9c2jx7ve0s2g7pg4fp3wkg7sqyk0zueyqj9jp5",
    "lightning": "wwbd@strike.me",
}

OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "qr"


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)
    for name, payload in PAYLOADS.items():
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
        out = OUT_DIR / f"{name}.svg"
        img.save(str(out))
        print(f"wrote {out.name}  <- {payload}")


if __name__ == "__main__":
    main()
