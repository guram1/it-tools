# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

OPS-BOX (ops-box.net) is a static site of free IT/network utilities. No build system, no package manager, no framework — plain HTML/CSS/JS served as static files. Deployed at `https://ops-box.net/`.

## Local development

There is no build or test step. To preview, serve the repo root over HTTP (relative paths like `../mac_db/...` require a real server, not `file://`):

```
python3 -m http.server 8000
# then open http://localhost:8000/
```

When adding or renaming a tool page, four files need to stay in sync — easy to miss:

1. `tools/<slug>.html` — the new file
2. `index.html` — add a `.tool-card` in the right `<section class="category">` AND bump the "curated collection of **N** free IT tools" count in the "Why OPS-BOX?" copy
3. `sitemap.xml` — append a `<url>` entry with today's `lastmod`
4. Footer `<div class="footer-section">` blocks in the new page AND a couple of sibling pages — these are hand-maintained per-file lists (Network / Security / Developer) and drift over time. Don't try to make them complete; keep them representative of the category.

## Tool-page template

Every tool under `tools/` follows the same structure — copy an existing tool when adding a new one rather than starting from scratch. The skeleton (top-to-bottom):

- GA snippet + `<meta>` SEO block (title, description, keywords, canonical, OG, Twitter)
- `<link>` to shared `css/style.css` (tool pages) — the homepage inlines its own styles instead
- Two `<script type="application/ld+json">` blocks: a `WebApplication` schema and a `FAQPage` schema (the FAQ entries must match the rendered `.faq-item` text below — keep both in sync)
- AdSense script tag with client ID `ca-pub-1924789684268835` (do not change without coordination)
- `<header>` with logo + 4-link `header-nav`
- `<main>` containing breadcrumb → `.tool-container` (the actual tool UI) → `.seo-content` (substantive prose, see SEO note below) → `.related-tools` grid
- `<footer>` with three `.footer-section` blocks
- Toast div + `<script src="../js/common.js"></script>` + per-tool `<script>` + FAQ toggle script

Tool logic is inlined per page. There is no JS bundler and no shared component layer beyond `js/common.js` (`showToast`, `copyToClipboard`, `initRangeSliders`, plus the URL-state helpers listed below).

The color theme is defined as CSS custom properties on `:root` (dark theme, green accent `#22c55e`) and is duplicated in `index.html`'s inline styles and `css/style.css`. Keep these in sync when changing theme colors.

## External services used by tools

All client-side — no backend code lives in this repo:

- `https://ssl-api.ops-box.net/` — own backend proxy for SSL check and DNS Dumpster (separate repo)
- `https://cloudflare-dns.com/dns-query` — DoH for DNS lookup
- `https://api.ipify.org` — caller's public IP
- `https://get.geojs.io/v1/ip/geo/` — IP geolocation; batch endpoint chunked for 1000-IP bulk lookups
- `https://stat.ripe.net/data/` — RIPEstat (BGP ASN lookup): `as-overview`, `announced-prefixes`, `asn-neighbours`, `network-info` (IP→ASN), `searchcomplete` (name→ASN). CORS-friendly, no API key.
- `https://cdn.jsdelivr.net/npm/bcryptjs@2.4.3/` — external runtime dep, loaded by `tools/bcrypt.html`.
- `https://cdn.jsdelivr.net/npm/node-forge@1.3.1/` — external runtime dep for ASN.1/PKI, loaded by `tools/csr-generator.html`, `tools/certificate-decoder.html`, `tools/csr-decoder.html`. Web Crypto can't build/parse PKCS#10 or X.509, so these three pages use node-forge. CSR keygen uses the async callback form of `forge.pki.rsa.generateKeyPair` (no web-worker file needed). All other tools are dependency-free.

Everything else (JWT sign/verify, HMAC, TOTP, hashing, IPv6 BigInt math) uses the browser Web Crypto API. The OpenSSL command generator (`tools/openssl-command-generator.html`) only builds command strings — it has no crypto and no dependencies.

## MAC vendor database (`mac_db/`)

`tools/mac-vendor-lookup.html` resolves OUIs from sharded JSON files in `mac_db/`. The shard key is the first 2 hex chars of the cleaned MAC (uppercase, e.g. `00.json`, `A4.json`); the file is an object keyed by the full 6-char OUI. Shards are lazy-loaded and cached in memory per session. If you regenerate this database, preserve the `{shardKey}.json` → `{OUI: "Vendor"}` layout or update the loader at `tools/mac-vendor-lookup.html:301`.

## Gotchas hit while building tools (do not re-discover)

- **IPv4 bitwise math:** JavaScript bitwise operations return signed int32, so `(s & mask) !== s` will spuriously fail for IPs ≥ `128.0.0.0`. Always wrap the result with `>>> 0` — see `tools/cidr-aggregator.html` `rangeToCidrs` and `parseLine` for the pattern.
- **IPv6 math:** use `BigInt` end-to-end (`tools/ipv6-subnet-calculator.html`). 32-bit shifts are not enough.
- **TOTP counter:** the HMAC counter is 64-bit. `DataView.setUint32(0, hi)` + `setUint32(4, lo)` — don't pack only the low 32 bits or codes will diverge from real authenticators past Jan 2038-ish, and also for non-standard step sizes.
- **JSON-LD ↔ visible FAQ:** the `FAQPage` JSON-LD block must mirror the rendered `<div class="faq-item">` text exactly. If you edit one, edit the other.

## SEO / content constraints

This site is on Google AdSense — past commits explicitly addressed an AdSense "low value content" violation (see `a4ff790`). When adding pages or trimming content, keep substantive descriptions/usage text on each tool page rather than reducing them to bare UI. Canonical URL, OG tags, Twitter card, and schema.org JSON-LD blocks are present on every page and should be kept for any new tool.

Absolute self-URLs (canonical, `og:url`, JSON-LD `url`, `sitemap.xml` `<loc>`) are **extensionless** (`https://ops-box.net/tools/<slug>`), because Cloudflare Pages 308-redirects `*.html` to the extensionless path. Relative internal links keep `.html` so `python3 -m http.server` previews still work.

`ads.txt` (AdSense seller line) and `404.html` (noindex, **no AdSense script**: Google forbids ads on error pages) live at the repo root. Without `404.html`, Cloudflare Pages serves `index.html` with status 200 for every unknown path, which creates soft-404s.

Contact email across the site is `contact@ops-box.net` (not a personal address — see commit `49d8184`).

## Site-wide conventions (2026-11-21 overhaul)

- Every page loads `/css/base.css?v=<ver>` LAST in `<head>` (self-hosted fonts from `/fonts/`, WCAG-AA `--text-muted`, unified header + mobile menu) and `/js/nav.js?v=<ver>` (defer) before the final `</body>`. The `<header>` markup is identical on every page; change it with a script across all files, never per page.
- `js/common.js` also provides `getToolParams()`, `setToolParams(obj)`, `copyShareLink()`, `debounce(fn, ms)`. Tools prefill an example, update live, and keep shareable state in the query string.
- Static assets are cached for a week (`_headers`): bump `?v=` on every `css/` / `js/` reference when you change those files.
- Renamed/removed pages get a 301 in `_redirects` (both `/path` and `/path.html`).
- `scripts/check_site.py` (also in CI, `.github/workflows/checks.yml`, with `html-validate`) checks JSON-LD, FAQ/JSON-LD match, internal links, sitemap vs pages, canonicals, titles <= 60, one H1, header/nav/base.css presence and SRI. Run it before every push.
- Site-wide regex inserts: use the LAST `</body>` (`rfind`); `tools/wifi-qr-generator.html` has `</body>` inside a JS print template.
