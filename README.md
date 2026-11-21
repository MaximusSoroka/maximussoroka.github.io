# Desire Agency

Static website: an honest, sourced recommendation of n8n, plus a directory of 19 automation and AI-agent tools. English is primary; German lives under `/de/`.

Live URL: [https://maximussoroka.github.io/](https://maximussoroka.github.io/)

## Pages

| Path | Content |
|---|---|
| `/` | Home (English) |
| `/n8n/` | n8n recommendation article |
| `/templates/` | Three free n8n workflow templates (English), with downloadable `workflow.json` files |
| `/directory/` | Tool directory |
| `/legal/` | Legal notice / Impressum |
| `/de/` | The same pages in German (the templates page is English-only) |
| `/llms.txt` | Short site map for language models |
| `/tools.json` | Machine-readable directory (EN+DE), no affiliate links, plus template and newsletter URLs |
| `/sitemap.xml` | URL list |

## Affiliate links

There are **no active affiliate links** at the moment. `N8N_AFFILIATE_URL` and `MAKE_AFFILIATE_URL` in `config.js` are empty, so product buttons go to the official vendor sites (`https://n8n.io/`, `https://www.make.com/`). The n8n partner application was declined on 19 November 2026; a later reapplication is planned.

To add an official partner URL later, set it in `config.js` and redeploy that file. A rebuild (`python3 build.py`) is not required for the link switch. Links then get `rel="sponsored nofollow"` and are labelled **#ad / Anzeige**. Do not invent links.

## Build

```bash
python3 build.py
```

Local preview:

```bash
python3 -m http.server 8080
```

Then open `http://127.0.0.1:8080/` (English) or `http://127.0.0.1:8080/de/` (German).

Prices and programme figures come from official public pages checked on 18 November 2026. No figures were invented. Own revenue: €0. The free Desire Agency newsletter sign-up is https://desireagency.beehiiv.com/subscribe (button label: “Get the build log”). This is a static site with no cookies, tracking or analytics.

The directory pages include schema.org JSON-LD (`ItemList` of `SoftwareApplication`). `/tools.json` is the canonical machine-readable copy of those entries; it does not include affiliate URLs or unpublished placeholder slots.

## Prepared, not public: /websites/ and /de/websites/

A preview of the planned website service (packages Vitrine, Atelier, Maison and Care, shown as "price on request"). It is **not linked anywhere**, is set to `noindex, nofollow` and is **not in sitemap.xml or llms.txt**.
To switch it on later, once the owner approves prices and launch:
1. In `build.py`, set the prices in `WEBSITES` (replace `price`) and add a contact action.
2. In `shell()`, remove the `noindex` case for `page == "websites"` and let it get hreflang links (the `page not in ("templates", "websites")` check).
3. Add `("websites", "Websites")` to `NAV` and a `"websites"` path to `page_paths()`, then add `/websites/` and `/de/websites/` to `write_sitemap()` and `write_llms_txt()`.
4. Run `python3 build.py` and push.
