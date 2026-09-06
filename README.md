# donate.grimnirworks.com

The GrimnirWorks tip jar. One static page, served by GitHub Pages at
**https://donate.grimnirworks.com**.

## Why this is a public repo

Because it publishes payment addresses, and **an address you cannot audit is an
address you should not send to.**

Keeping the page in a public repo means the Bitcoin address, the Lightning
address, and every outbound link have a git history: who changed them, when, and
to what. If one of them is ever quietly swapped, the swap is a commit — visible,
dated, and diffable — rather than an invisible edit to a live page. Anyone about
to send money can check the address here against the address on screen, and check
that it has not moved since the last time they looked.

That property only holds if the page stays boring, so it does:

- **One file.** `index.html` — plain HTML, CSS and a few lines of inline vanilla
  JavaScript for the copy buttons.
- **No build step, no npm, no framework, no JS dependency.** Nothing sits between
  the source in this repo and the bytes the browser renders.
- **No external requests at load.** No CDN, no font host, no analytics, no
  runtime QR service. The page fetches nothing, so there is nothing to intercept
  and nothing to swap.
- **QR codes are committed, not generated.** `qr/*.svg` are static files. They
  are SVG rather than PNG on purpose: SVG is text, so a tampered QR shows up as a
  readable diff instead of an opaque binary blob.

Every dependency this page could have had would be one more place an address
could be changed without touching this repo. So it has none.

## Layout

```
index.html          the entire page
qr/bitcoin.svg      QR for the on-chain address
qr/lightning.svg    QR for the Lightning address
CNAME               donate.grimnirworks.com
tools/make_qr.py    regenerates qr/*.svg from the addresses
tools/verify.py     independently proves the committed QRs are correct
```

`tools/` is developer-only. It is never served and never loaded by the page.

## Regenerating the QR codes

Only needed if an address actually changes.

```bash
pip install -r tools/requirements.txt
python tools/make_qr.py     # rewrite qr/*.svg from the addresses in the script
python tools/verify.py      # then prove the result
```

`verify.py` does not trust `make_qr.py`. It reads the `.svg` files as they exist
on disk, rasterises them itself, decodes them with OpenCV — a completely separate
code path from the one that wrote them — and checks that each decodes to exactly
the address printed beside it in `index.html`. It also fails if `index.html` ever
grows an external subresource. Exit code `0` means the page is consistent with
itself.

Each QR encodes **exactly** the string shown as selectable text next to it: no
`bitcoin:` URI wrapper, no amount, no label. What you scan and what you read are
the same bytes, which is what makes a by-eye audit meaningful.

## The rails

| # | Rail | Where it goes |
|---|------|---------------|
| 1 | Bitcoin (on-chain) | native SegWit / bech32, mainnet only |
| 2 | Lightning | `wwbd@strike.me` |
| 3 | X Money | [@WWBD01_Freedom](https://x.com/WWBD01_Freedom) |
| 4 | GitHub Sponsors | [OdinKara](https://github.com/sponsors/OdinKara) — pending approval, may 404 |

Nothing in any GrimnirWorks project is paywalled, and nothing about this page
changes that. It is a tip jar.

## License

The page content is © GrimnirWorks / GrimnirWorks. Do not reuse it with these
addresses substituted.
