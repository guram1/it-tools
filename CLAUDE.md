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

When adding or renaming a tool page, also update:
- `index.html` — the tools grid on the landing page
- `sitemap.xml` — the URL list
- Internal links in sibling tool pages if they cross-reference

## Architecture

Each tool is a fully self-contained HTML file under `tools/`. There is no shared template, no component system, and no JS bundler. A tool page typically inlines its own `<style>` and `<script>` blocks rather than sharing CSS/JS across pages — only two shared assets exist:

- `css/style.css` — shared styles used by tool pages (the homepage inlines its own styles)
- `js/common.js` — only three helpers: `showToast()`, `copyToClipboard(id)`, and `initRangeSliders()` (auto-runs on DOMContentLoaded)

The color theme is defined as CSS custom properties on `:root` (dark theme, green accent `#22c55e`) and is duplicated in `index.html`'s inline styles and `css/style.css`. Keep these in sync when changing theme colors.

Every page includes the same Google Analytics snippet (`G-FH74PGMNYD`) inlined in `<head>`, plus its own `<script type="application/ld+json">` structured data block with the tool's name/description.

### External APIs used by tools

Client-side calls (no backend code in this repo):
- `https://ssl-api.ops-box.net/` — own backend proxy for SSL check and DNS Dumpster (lives outside this repo)
- `https://cloudflare-dns.com/dns-query` — DoH for DNS lookup
- `https://api.ipify.org` — caller's public IP
- `https://get.geojs.io/v1/ip/geo/` — IP geolocation; supports a batch endpoint used to chunk bulk lookups (current cap: 1000 IPs via parallel chunked requests — see commit history before changing)

### MAC vendor database (`mac_db/`)

`tools/mac-vendor-lookup.html` resolves OUIs from sharded JSON files in `mac_db/`. The shard key is the first 2 hex chars of the cleaned MAC (uppercase, e.g. `00.json`, `A4.json`); the file is an object keyed by the full 6-char OUI. Shards are lazy-loaded and cached in memory per session. If you regenerate this database, preserve the `{shardKey}.json` → `{OUI: "Vendor"}` layout or update the loader at `tools/mac-vendor-lookup.html:301`.

## SEO / content constraints

This site is on Google AdSense — past commits explicitly addressed an AdSense "low value content" violation (see `a4ff790`). When adding pages or trimming content, keep substantive descriptions/usage text on each tool page rather than reducing them to bare UI. Canonical URL, OG tags, Twitter card, and schema.org JSON-LD blocks are present on every page and should be kept for any new tool.

Contact email across the site is `contact@ops-box.net` (not a personal address — see commit `49d8184`).
