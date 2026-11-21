#!/usr/bin/env python3
"""Build the static Desire Agency site from local source files.

Does not publish, push, or create a repository.
Run from this directory: python3 build.py
"""
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
TOOLS = json.loads((DATA / "tools.json").read_text())
TOOLS_EN = json.loads((DATA / "tools_en.json").read_text())
PRUEF = "18.11.2026"
PRUEF_EN = "18 November 2026"
N_TOOLS = int(TOOLS.get("n_eintraege") or len(TOOLS["tools"]))

def esc(s) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def prefix(depth: int) -> str:
    return "" if depth == 0 else "../" * depth


def tool_view(src: dict, lang: str) -> dict:
    en = TOOLS_EN.get(src["id"], {})
    if lang == "en":
        return {
            **src,
            "kategorie": en.get("kategorie") or src["kategorie"],
            "kurz": en.get("kurz") or src["kurz"],
            "preis": en.get("preis") or src["preis"],
            "preis_status": en.get("preis_status") or src["preis_status"],
            "affiliate_detail": en.get("affiliate_detail") or src["affiliate_detail"],
        }
    return src


def group_of(t: dict) -> str:
    cat = (t.get("kategorie") or "").lower()
    if "ki-" in cat or cat.startswith("ai ") or "/ ai" in cat or "ai agents" in cat or "ai apps" in cat or "ai development" in cat or "ai workflow" in cat:
        return "ai"
    return "automation"


def status_class(status: str) -> str:
    s = (status or "").lower()
    if "unbekannt" in s or s == "unknown":
        return "badge-unknown"
    if "teilweise" in s or "partial" in s or "vorbehalt" in s or "caveat" in s:
        return "badge-partial"
    return ""


# ---------------------------------------------------------------------------
# Shared chrome
# ---------------------------------------------------------------------------

NAV = {
    "en": [
        ("home", "Home"),
        ("n8n", "Recommend n8n"),
        ("templates", "Templates"),
        ("directory", "Directory"),
        ("websites", "Websites"),
        ("legal", "Legal notice"),
    ],
    "de": [
        ("home", "Start"),
        ("n8n", "n8n-Empfehlung"),
        ("templates", "Templates"),
        ("directory", "Verzeichnis"),
        ("websites", "Websites"),
        ("legal", "Impressum"),
    ],
}

SUBSCRIBE_URL = "https://desireagency.beehiiv.com/subscribe"
SUBSCRIBE_LABEL = {
    "en": "Get the build log",
    "de": "Build-Log abonnieren",
}

BANNER = {
    "en": (
        "This page may contain affiliate links in the future. Those links will be labelled "
        "<strong>#ad / Anzeige</strong>. No earnings promises. Prices checked on {d}. "
        "Our own revenue so far: €0."
    ).format(d=PRUEF_EN),
    "de": (
        "Diese Seite kann in Zukunft Affiliate-Links enthalten. Solche Links werden als "
        "<strong>#ad / Anzeige</strong> gekennzeichnet. Kein Gewinnversprechen. Preise geprüft am {d}. "
        "Unser eigener Ertrag bisher: 0&nbsp;€."
    ).format(d=PRUEF),
}

FOOT = {
    "en": (
        f"Prices and programme terms as of {PRUEF_EN}, from the vendors’ official pages. "
        "Not financial advice. Our own revenue: €0."
    ),
    "de": (
        f"Stand der Preise und Programmbedingungen: {PRUEF}, offizielle Seiten der Anbieter. "
        "Keine Finanzberatung. Eigener Ertrag: 0 €."
    ),
}


def page_paths(lang: str, depth: int) -> dict:
    p = prefix(depth)
    if lang == "en":
        return {
            "home": "./" if depth == 0 else p,
            "n8n": p + "n8n/",
            "templates": p + "templates/",
            "directory": p + "directory/",
            "websites": p + "websites/",
            "legal": p + "legal/",
            "other_lang": p + "de/" if depth == 0 else (p + "de/" if depth == 1 else "../../de/"),
            "config": p + "config.js",
            "css": p + "css/site.css",
            "js_aff": p + "js/affiliate.js",
            "js_dir": p + "js/directory.js",
        }
    # German lives under /de/
    if depth == 1:  # /de/index.html
        return {
            "home": "./",
            "n8n": "./n8n/",
            "templates": "../templates/",
            "directory": "./directory/",
            "websites": "./websites/",
            "legal": "./legal/",
            "other_lang": "../",
            "config": "../config.js",
            "css": "../css/site.css",
            "js_aff": "../js/affiliate.js",
            "js_dir": "../js/directory.js",
        }
    # depth 2: /de/n8n/ etc.
    return {
        "home": "../",
        "n8n": "../n8n/",
        "templates": "../../templates/",
        "directory": "../directory/",
        "websites": "../websites/",
        "legal": "../legal/",
        "other_lang": "../../",
        "config": "../../config.js",
        "css": "../../css/site.css",
        "js_aff": "../../js/affiliate.js",
        "js_dir": "../../js/directory.js",
    }


def lang_href(lang: str, page: str, depth: int) -> str:
    """URL of the same page in the other language."""
    # Templates exist in English only; the DE language switch goes to the German home.
    if page == "websites":
        return "../de/websites/" if lang == "en" else "../../websites/"
    if page == "templates":
        if lang == "en":
            return "../de/" if depth >= 1 else "de/"
        return "../templates/" if depth == 1 else "../../templates/"
    if lang == "en":
        if depth == 0:
            return {"home": "de/", "n8n": "de/n8n/", "directory": "de/directory/", "legal": "de/legal/"}[page]
        return {"home": "../de/", "n8n": "../de/n8n/", "directory": "../de/directory/", "legal": "../de/legal/"}[page]
    if depth == 1:
        return {"home": "../", "n8n": "../n8n/", "directory": "../directory/", "legal": "../legal/"}[page]
    return {
        "home": "../",
        "n8n": "../../n8n/",
        "directory": "../../directory/",
        "legal": "../../legal/",
    }[page]


GUIDE_URL = "https://desireagencyai.gumroad.com/l/blhhwg"
JOURNAL_URL = "https://desireagencyai.gumroad.com/l/htrxgl"
X_URL = "https://x.com/desire__agency"
DEVTO_URL = "https://dev.to/desire_agency"
IH_URL = "https://www.indiehackers.com/desireagency"
NUMBERS_AS_OF = {"en": "21 Nov 2026, 19:25 Lisbon", "de": "21.11.2026, 19:25 Lissabon"}

LOGO_SVG = (
    '<svg class="brand-mark" viewBox="0 0 64 64" aria-hidden="true" focusable="false">'
    '<defs><linearGradient id="dg" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0" stop-color="#7c6cff"/><stop offset="1" stop-color="#4b3be0"/></linearGradient></defs>'
    '<rect width="64" height="64" rx="16" fill="url(#dg)"/>'
    '<path d="M20 16h12c10 0 16 6.5 16 16s-6 16-16 16H20V16Zm8 7v18h4c5.3 0 8-3.2 8-9s-2.7-9-8-9h-4Z" fill="#fff"/>'
    '</svg>'
)

ICON = {
    "x": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231 5.45-6.231Zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77Z"/></svg>',
    "devto": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7.42 10.05c-.18-.16-.46-.23-.84-.23H6v4.36h.58c.37 0 .66-.08.84-.23.2-.16.29-.4.29-.73v-2.44c0-.33-.1-.57-.29-.73ZM0 4.94v14.12h24V4.94H0Zm8.56 8.6c0 .67-.2 1.18-.62 1.53-.4.36-.98.53-1.72.53H4.71V8.4h1.56c.72 0 1.28.18 1.68.54.4.35.61.86.61 1.52v3.08Zm3.86-3.88h-1.78v1.27h1.09v1.27h-1.09v1.27h1.78v1.27H10.3c-.4 0-.74-.32-.75-.73V9.14c0-.4.32-.74.73-.75h2.14v1.27Zm3.48 4.94c-.58 1.35-1.61 1.08-2.07 0l-1.68-6.2h1.43l1.3 4.89 1.3-4.89h1.43l-1.71 6.2Z"/></svg>',
    "ih": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="1" y="1" width="22" height="22" rx="5" fill="currentColor"/><path d="M7 7h2.2v10H7zM11.6 7h2.2v3.9h2.4V7h2.2v10h-2.2v-4h-2.4v4h-2.2z" fill="var(--surface)"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>',
    "book": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 19.5V5a2 2 0 0 1 2-2h14v16H6.5A2.5 2.5 0 0 0 4 21.5v-2Z"/><path d="M8 7h8M8 11h6"/></svg>',
    "sheet": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18"/></svg>',
    "flow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="6" height="6" rx="1.5"/><rect x="15" y="15" width="6" height="6" rx="1.5"/><rect x="15" y="3" width="6" height="6" rx="1.5"/><path d="M9 6h6M18 9v6"/></svg>',
}

CANONICAL = {
    ("en", "home"): "/", ("en", "n8n"): "/n8n/", ("en", "templates"): "/templates/",
    ("en", "directory"): "/directory/", ("en", "legal"): "/legal/",
    ("de", "home"): "/de/", ("de", "n8n"): "/de/n8n/", ("de", "directory"): "/de/directory/",
    ("de", "legal"): "/de/legal/",
    ("en", "websites"): "/websites/", ("de", "websites"): "/de/websites/",
}

FOOTER_TEXT = {
    "en": {
        "about": "An AI agent team, built in public from Lisbon. We publish the real numbers, including the zeros.",
        "site": "Site", "products": "Products", "follow": "Follow",
        "guide": "Agent Team Guide", "journal": "Free trading journal", "templates": "Free n8n templates",
        "newsletter": "Newsletter",
    },
    "de": {
        "about": "Ein KI-Agenten-Team, öffentlich aufgebaut in Lissabon. Wir zeigen die echten Zahlen, auch die Nullen.",
        "site": "Seite", "products": "Produkte", "follow": "Folgen",
        "guide": "Agent-Team-Guide (EN)", "journal": "Kostenloses Trading-Journal", "templates": "Kostenlose n8n-Vorlagen",
        "newsletter": "Newsletter",
    },
}


def shell(lang: str, page: str, depth: int, title: str, description: str, body: str, extra_js: str = "", extra_head: str = "") -> str:
    paths = page_paths(lang, depth)
    root = paths["css"][: -len("css/site.css")]
    nav = []
    for key, label in NAV[lang]:
        if key == "legal":
            continue  # legal lives in the footer
        href = paths[key]
        cur = ' aria-current="page"' if key == page else ""
        nav.append(f'<a href="{href}"{cur}>{esc(label)}</a>')
    other = "Deutsch" if lang == "en" else "English"
    other_href = lang_href(lang, page, depth)
    en_cur = ' aria-current="true"' if lang == "en" else ""
    de_cur = ' aria-current="true"' if lang == "de" else ""
    wrap = "wrap-narrow" if page in ("n8n", "legal", "templates") else "wrap"
    dir_js = f'\n<script src="{paths["js_dir"]}" defer></script>' if page == "directory" else ""
    progress = '\n  <div class="progress" aria-hidden="true"></div>' if page in ("n8n", "templates", "legal") else ""
    canon = site_url(CANONICAL[(lang, page)])
    alt = ""
    if page != "templates":
        en_url = site_url(CANONICAL[("en", page)])
        de_url = site_url(CANONICAL[("de", page)])
        alt = (
            f'  <link rel="alternate" hreflang="en" href="{en_url}">\n'
            f'  <link rel="alternate" hreflang="de" href="{de_url}">\n'
            f'  <link rel="alternate" hreflang="x-default" href="{en_url}">\n'
        )
    og_img = site_url("/img/og.png") if (ROOT / "img" / "og.png").exists() else site_url("/og.png")
    # Binary assets are added separately; only reference them once they exist in the repo.
    og_tags = tw_img = png_icons = ""
    if (ROOT / "img" / "og.png").exists() or (ROOT / "og.png").exists():
        og_tags = (f'  <meta property="og:image" content="{og_img}">\n'
                   '  <meta property="og:image:width" content="1200">\n'
                   '  <meta property="og:image:height" content="630">\n')
        tw_img = f'  <meta name="twitter:image" content="{og_img}">\n'
    if (ROOT / "favicon-32.png").exists():
        png_icons += f'  <link rel="icon" href="{root}favicon-32.png" sizes="32x32" type="image/png">\n'
    if (ROOT / "apple-touch-icon.png").exists():
        png_icons += f'  <link rel="apple-touch-icon" href="{root}apple-touch-icon.png">\n'
    f = FOOTER_TEXT[lang]
    sub_label = SUBSCRIBE_LABEL[lang]
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index, follow">
  <meta name="description" content="{esc(description)}">
  <title>{esc(title)}</title>
  <link rel="canonical" href="{canon}">
{alt}  <meta name="theme-color" content="#0c0d12">
  <link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
{png_icons}  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Desire Agency">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{canon}">
{og_tags}  <meta property="og:locale" content="{"en_US" if lang == "en" else "de_DE"}">
  <meta name="twitter:card" content="{"summary_large_image" if og_tags else "summary"}">
  <meta name="twitter:site" content="@desire__agency">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
{tw_img}  <script>try{{var t=localStorage.getItem("theme");if(t==="dark"||t==="light")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
  <link rel="stylesheet" href="{root}fonts/inter.css" media="print" onload="this.media='all'">
  <noscript><link rel="stylesheet" href="{root}fonts/inter.css"></noscript>
  <link rel="stylesheet" href="{paths['css']}">
{extra_head}</head>
<body>
  <a class="skip" href="#content">{"Skip to content" if lang == "en" else "Zum Inhalt"}</a>
  <header class="site-header">
    <div class="header-inner wrap">
      <a class="brand" href="{paths['home']}">
        {LOGO_SVG}
        <span class="brand-text">
          <span class="brand-name">Desire<span class="wm-2"> Agency</span></span>
          <span class="brand-tag">{"An AI agent team, built in public" if lang == "en" else "KI-Agenten-Team, öffentlich gebaut"}</span>
        </span>
      </a>
      <nav aria-label="{"Main" if lang == "en" else "Hauptnavigation"}">
        {''.join(nav)}
        <a class="btn btn-primary btn-sm nav-cta" href="{esc(SUBSCRIBE_URL)}">{esc(sub_label)}</a>
        <span class="lang" aria-label="Language">
          <a href="{other_href if lang == "de" else "#"}"{en_cur} hreflang="en">EN</a>
          <a href="{other_href if lang == "en" else "#"}"{de_cur} hreflang="de">DE</a>
        </span>
      </nav>
      <button type="button" class="theme-toggle" aria-label="{"Toggle theme" if lang == "en" else "Design wechseln"}">{THEME_ICONS}</button>
    </div>
  </header>{progress}
  <div class="ad-banner">
    <div class="wrap">{BANNER[lang]}</div>
  </div>
  <main id="content">
    <div class="{wrap}">
{body}
    </div>
  </main>
  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-grid">
        <div class="footer-brand">
          <a class="brand" href="{paths['home']}">{LOGO_SVG}<span class="brand-text"><span class="brand-name">Desire<span class="wm-2"> Agency</span></span></span></a>
          <p>{esc(f["about"])}</p>
          <div class="socials">
            <a href="{X_URL}" rel="me noopener" aria-label="X (@desire__agency)">{ICON["x"]}</a>
            <a href="{DEVTO_URL}" rel="me noopener" aria-label="dev.to">{ICON["devto"]}</a>
            <a href="{IH_URL}" rel="me noopener" aria-label="Indie Hackers">{ICON["ih"]}</a>
            <a href="{esc(SUBSCRIBE_URL)}" rel="noopener" aria-label="{esc(f["newsletter"])}">{ICON["mail"]}</a>
          </div>
        </div>
        <div class="footer-col">
          <h3>{esc(f["site"])}</h3>
          <ul>
            <li><a href="{paths['home']}">{esc(NAV[lang][0][1])}</a></li>
            <li><a href="{paths['n8n']}">{esc(NAV[lang][1][1])}</a></li>
            <li><a href="{paths['directory']}">{esc(NAV[lang][3][1])}</a></li>
            <li><a href="{paths['websites']}">Websites</a></li>
            <li><a href="{paths['legal']}">{"Legal notice / Impressum" if lang == "en" else "Impressum / Kontakt"}</a></li>
            <li><a href="{other_href}">{other}</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3>{esc(f["products"])}</h3>
          <ul>
            <li><a href="{GUIDE_URL}" rel="noopener">{esc(f["guide"])}</a></li>
            <li><a href="{JOURNAL_URL}" rel="noopener">{esc(f["journal"])}</a></li>
            <li><a href="{paths['templates']}">{esc(f["templates"])}</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h3>{esc(f["follow"])}</h3>
          <ul>
            <li><a href="{esc(SUBSCRIBE_URL)}" rel="noopener">{esc(f["newsletter"])}</a></li>
            <li><a href="{X_URL}" rel="me noopener">X · @desire__agency</a></li>
            <li><a href="{DEVTO_URL}" rel="me noopener">dev.to</a></li>
            <li><a href="{IH_URL}" rel="me noopener">Indie Hackers</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>{esc(FOOT[lang])}</p>
        <p>© 2026 Desire Agency · Lisboa · {"No cookies, no tracking." if lang == "en" else "Keine Cookies, kein Tracking."}</p>
      </div>
    </div>
  </footer>
  <script src="{paths['config']}"></script>
  <script src="{paths['js_aff']}"></script>{dir_js}
  <script src="{root}js/site.js" defer></script>{extra_js}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

HOME = {
    "en": {
        "title": "Desire Agency — an AI agent team, built in public",
        "description": "One person and a team of AI agents, built in public from Lisbon. Real numbers including the zeros, free n8n templates, a sourced tool directory and an honest guide.",
        "eyebrow": "Building in public from Lisbon",
        "h1_a": "One person. A team of AI agents.",
        "h1_b": "Every number in public.",
        "lede": "We are building an autonomous AI agent team and writing down what actually happens: what ships, what breaks, and what it earns. Right now that is €0, and we say so.",
        "cta_news": "Get the build log",
        "cta_guide": "Read the guide — $19",
        "link_tpl": "Free n8n templates",
        "link_journal": "Free trading journal",
        "link_n8n": "Why we recommend n8n",
        "hero_note": "No earnings promises. Not financial advice.",
        "ledger_title": "Ledger",
        "ledger": [
            ("Real revenue", "€0.00", ""),
            ("Sales so far", "0", ""),
            ("Server cost", "€6.14 / mo", ""),
            ("Paper-trading P&amp;L (simulated)", "−$53.68", "neg"),
        ],
        "ledger_foot": "Paper trading uses simulated money only. It is not income.",
        "bip_kicker": "Build in public",
        "bip_title": "The honest numbers",
        "bip_text": "No vanity metrics and no testimonials we don’t have. These are the figures from our own logs.",
        "stats": [
            ("11", "AI agents", "10 specialist bots and one chief of staff, coordinated by one person."),
            ("83", "Closed paper trades", "Across four paper-trading desks. Closed P&amp;L −$53.68, simulated money."),
            ("3", "Free n8n templates", "Importable workflow.json files with placeholder credentials."),
            (str(N_TOOLS), "Tools sourced", f"Automation and AI-agent tools, prices from official pages ({PRUEF_EN})."),
        ],
        "shipped_title": "Shipped recently",
        "shipped": [
            ("20 Nov", "Three free n8n templates and the newsletter sign-up."),
            ("21 Nov", "The Agent Team Guide on Gumroad and newsletter issue #1."),
            ("21 Nov", "A free trading journal and risk sheet."),
            ("21 Nov", "Profiles on dev.to and Indie Hackers."),
        ],
        "rules_title": "House rules",
        "rules": [
            "Real numbers only, including the zeros.",
            "No earnings promises, no coin tips, no financial advice.",
            "Affiliate links, if any, are labelled #ad / Anzeige.",
            "This site sets no cookies and runs no tracking.",
        ],
        "prod_kicker": "Products",
        "prod_title": "Start here",
        "prod_text": "One paid guide, two free resources. All of them come out of what we actually run.",
        "products": [
            {
                "icon": "book", "pill": "Guide", "featured": True,
                "title": "How I Built a Self-Improving AI Agent Team",
                "text": "A field report, not a demo: how one person works with ten AI agents, what each one does, and what went wrong.",
                "price": "$19", "price_sub": "$9 with code <code>EARLYBIRD</code>",
                "cta": "Get the guide", "url": GUIDE_URL,
            },
            {
                "icon": "sheet", "pill": "Free", "featured": False,
                "title": "Trading Journal + Risk Sheet",
                "text": "Log every closed trade and check whether you follow your own rules. Sizes positions from your stop and risk per trade. Excel and Google Sheets.",
                "price": "$0", "price_sub": "Free download on Gumroad",
                "cta": "Get the journal", "url": JOURNAL_URL,
            },
            {
                "icon": "flow", "pill": "Free", "featured": False,
                "title": "Three n8n templates",
                "text": "A daily RSS digest, a form that writes to Google Sheets, and an uptime check that retries once after 60 seconds before alerting.",
                "price": "$0", "price_sub": "workflow.json, placeholder credentials",
                "cta": "Open the templates", "url": "@templates",
            },
        ],
        "n8n_kicker": "Tools we use",
        "n8n_title": "Why we recommend n8n",
        "n8n_text": "And when Make is still a fair fit. An honest, sourced guide to automation and agent workflows. Sources checked on 18 November 2026.",
        "cta1": "Read the recommendation",
        "cta2": f"Browse {N_TOOLS} tools",
        "cta_n8n": "See n8n",
        "facts_title": "What the official pages said on 18 November 2026",
        "facts": [
            ("Cloud pricing", "n8n Starter is €20/month, Pro €50/month, Business €667/month — each billed annually on the official pricing page. Monthly prices were not stated as figures."),
            ("Self-hosting and data", "The Community Edition for self-hosting is free on GitHub. For hosted cloud plans, n8n names Frankfurt (EU) as the storage location. 14-day trial, without a credit card according to the pricing page."),
            ("When Make may fit better", "Make’s free plan includes 1,000 credits per month. Paid-plan prices were not reliably readable, so they are not listed here. Whether the same workflow is cheaper on Make or n8n depends on the concrete flow — that is not proven in general."),
        ],
        "dir_title": "Tool directory",
        "dir_text": f"A sourced directory of {N_TOOLS} automation and AI-agent tools. Prices come only from official public pages dated {PRUEF_EN}. Where a figure was not readable, it is marked unknown. n8n is listed first on purpose.",
        "dir_cta": "Open the directory",
        "rev": "This is not financial advice and not a trading product. Our own revenue from these pages so far: €0.",
        "news_title": "The build log",
        "news_text": "A short, free newsletter from Desire Agency about what we are actually building — including these templates, the site, and the rest of the system. No earnings promises. Our own revenue so far: €0.",
        "news_cta": "Get the build log",
        "follow_text": "Or follow along:",
    },
    "de": {
        "title": "Desire Agency — ein KI-Agenten-Team, öffentlich gebaut",
        "description": "Eine Person und ein Team aus KI-Agenten, öffentlich aufgebaut in Lissabon. Echte Zahlen inklusive der Nullen, kostenlose n8n-Vorlagen, ein Tool-Verzeichnis mit Quellen und ein ehrlicher Guide.",
        "eyebrow": "Öffentlich gebaut in Lissabon",
        "h1_a": "Eine Person. Ein Team aus KI-Agenten.",
        "h1_b": "Jede Zahl öffentlich.",
        "lede": "Wir bauen ein autonomes KI-Agenten-Team und schreiben auf, was wirklich passiert: was live geht, was kaputtgeht und was es einbringt. Im Moment sind das 0 €, und das sagen wir auch.",
        "cta_news": "Build-Log abonnieren",
        "cta_guide": "Zum Guide — 19 $",
        "link_tpl": "Kostenlose n8n-Vorlagen",
        "link_journal": "Kostenloses Trading-Journal",
        "link_n8n": "Warum wir n8n empfehlen",
        "hero_note": "Kein Gewinnversprechen. Keine Finanzberatung.",
        "ledger_title": "Kassenbuch",
        "ledger": [
            ("Echter Ertrag", "0,00 €", ""),
            ("Verkäufe bisher", "0", ""),
            ("Serverkosten", "6,14 € / Monat", ""),
            ("Papier-Trading (simuliert)", "−53,68 $", "neg"),
        ],
        "ledger_foot": "Papier-Trading nutzt nur Spielgeld. Es ist kein Einkommen.",
        "bip_kicker": "Build in Public",
        "bip_title": "Die ehrlichen Zahlen",
        "bip_text": "Keine Schönwetter-Kennzahlen und keine Kundenstimmen, die wir nicht haben. Das sind die Werte aus unseren eigenen Logs.",
        "stats": [
            ("11", "KI-Agenten", "10 spezialisierte Bots und ein Chief of Staff, koordiniert von einer Person."),
            ("83", "Geschlossene Papier-Trades", "Auf vier Papier-Desks. Ergebnis −53,68 $, nur Spielgeld."),
            ("3", "Kostenlose n8n-Vorlagen", "Importierbare workflow.json-Dateien mit Platzhaltern für Zugangsdaten."),
            (str(N_TOOLS), "Tools mit Quellen", f"Automatisierungs- und KI-Agenten-Tools, Preise von offiziellen Seiten ({PRUEF})."),
        ],
        "shipped_title": "Zuletzt veröffentlicht",
        "shipped": [
            ("20.11.", "Drei kostenlose n8n-Vorlagen und die Newsletter-Anmeldung."),
            ("21.11.", "Der Agent-Team-Guide auf Gumroad und Newsletter-Ausgabe #1."),
            ("21.11.", "Ein kostenloses Trading-Journal mit Risiko-Rechner."),
            ("21.11.", "Profile auf dev.to und Indie Hackers."),
        ],
        "rules_title": "Unsere Regeln",
        "rules": [
            "Nur echte Zahlen, auch die Nullen.",
            "Kein Gewinnversprechen, keine Coin-Tipps, keine Finanzberatung.",
            "Affiliate-Links, falls es welche gibt, sind als #ad / Anzeige markiert.",
            "Diese Seite setzt keine Cookies und hat kein Tracking.",
        ],
        "prod_kicker": "Produkte",
        "prod_title": "Hier anfangen",
        "prod_text": "Ein bezahlter Guide, zwei kostenlose Ressourcen. Alles stammt aus dem, was wir selbst betreiben.",
        "products": [
            {
                "icon": "book", "pill": "Guide · EN", "featured": True,
                "title": "How I Built a Self-Improving AI Agent Team",
                "text": "Ein Praxisbericht statt einer Demo: wie eine Person mit zehn KI-Agenten arbeitet, was jeder davon macht und was schiefging. Auf Englisch.",
                "price": "19 $", "price_sub": "9 $ mit Code <code>EARLYBIRD</code>",
                "cta": "Zum Guide", "url": GUIDE_URL,
            },
            {
                "icon": "sheet", "pill": "Kostenlos", "featured": False,
                "title": "Trading-Journal + Risiko-Sheet",
                "text": "Jeden geschlossenen Trade festhalten und prüfen, ob du deine eigenen Regeln einhältst. Berechnet die Positionsgröße aus Stop und Risiko. Für Excel und Google Sheets.",
                "price": "0 $", "price_sub": "Kostenlos auf Gumroad",
                "cta": "Zum Journal", "url": JOURNAL_URL,
            },
            {
                "icon": "flow", "pill": "Kostenlos", "featured": False,
                "title": "Drei n8n-Vorlagen",
                "text": "Ein täglicher RSS-Digest, ein Formular in Google Sheets und eine Erreichbarkeitsprüfung, die nach 60 Sekunden einmal erneut prüft, bevor sie alarmiert. Seite auf Englisch.",
                "price": "0 $", "price_sub": "workflow.json, nur Platzhalter",
                "cta": "Zu den Vorlagen", "url": "@templates",
            },
        ],
        "n8n_kicker": "Tools, die wir nutzen",
        "n8n_title": "Warum wir n8n empfehlen",
        "n8n_text": "Und wann Make trotzdem passt. Ein ehrlicher, quellenbelegter Text zu Automatisierung und Agenten-Workflows. Quellenstand: 18.11.2026.",
        "cta1": "Empfehlung lesen",
        "cta2": f"{N_TOOLS} Tools ansehen",
        "cta_n8n": "n8n ansehen",
        "facts_title": "Was die offiziellen Seiten am 18.11.2026 sagten",
        "facts": [
            ("Cloud-Preise", "n8n Starter kostet 20 €/Monat, Pro 50 €/Monat, Business 667 €/Monat — jeweils laut offizieller Preisseite bei jährlicher Abrechnung. Monatliche Preise standen dort nicht als Zahl."),
            ("Selbst hosten und Datenort", "Die Community Edition zum Selbst-Hosten ist kostenlos auf GitHub. Für die gehosteten Cloud-Pläne nennt n8n Frankfurt (EU) als Speicherort. 14 Tage testen, laut Preisseite ohne Kreditkarte."),
            ("Wo Make besser passen kann", "Im Free-Plan nennt Make 1.000 Credits pro Monat. Preise der Bezahlpläne waren nicht zuverlässig ablesbar und stehen deshalb hier nicht. Ob derselbe Ablauf bei Make oder n8n günstiger ist, hängt vom konkreten Workflow ab — das ist nicht pauschal belegt."),
        ],
        "dir_title": "Tool-Verzeichnis",
        "dir_text": f"Ein quellenbelegtes Verzeichnis mit {N_TOOLS} Automatisierungs- und KI-Agenten-Tools. Preise nur aus öffentlichen offiziellen Seiten vom {PRUEF}. Wo ein Betrag nicht ablesbar war, steht unbekannt. n8n steht absichtlich zuerst.",
        "dir_cta": "Zum Verzeichnis",
        "rev": "Keine Finanzberatung, kein Trading-Produkt. Unser eigener Ertrag aus diesen Seiten bisher: 0 €.",
        "news_title": "Das Build-Log",
        "news_text": "Ein kurzer, kostenloser Newsletter von Desire Agency über das, was wir tatsächlich bauen — Vorlagen, die Website und den Rest des Systems. Kein Gewinnversprechen. Unser eigener Ertrag bisher: 0 €.",
        "news_cta": "Build-Log abonnieren",
        "follow_text": "Oder folge uns:",
    },
}


THEME_ICONS = (
    '<svg class="i-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/></svg>'
    '<svg class="i-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
)

TEAM = {
    "en": {
        "kicker": "The team", "title": "Who does what",
        "text": "One human owner, one chief of staff, and ten specialist agents. Hover or tap an agent to see its job.",
        "trade": "Trading desk (paper money)", "growth": "Growth & products", "lead_grp": "Coordination", "human_grp": "Owner",
        "hint": "Lines show who reports to the chief of staff.",
        "human": ("Desire", "Human owner", "Sets the goals and approves anything involving real money, purchases or deals."),
        "lead": ("Jojo", "Chief of staff", "Plans the day, hands out work, checks results and writes the morning and evening reports."),
        "trade_agents": [
            ("Chef", "Desk manager", "Runs the paper-trading desks and proposes rule changes."),
            ("Scout", "Candidate scout", "Looks for new candidates for the paper-trading desks."),
            ("News", "News watch", "Tracks news that could matter for the desks."),
            ("Charts", "Chart reader", "Reads price charts and market structure."),
            ("Skeptiker", "The skeptic", "Argues against ideas before they ship and looks for the weak spot."),
        ],
        "growth_agents": [
            ("Publisher", "Content & community", "Drafts posts and replies for X, Reddit and the newsletter."),
            ("Produkte", "Products", "Builds and maintains the Gumroad products and templates."),
            ("Analyst", "Social analyst", "Reads post performance and niche data, and suggests ideas. Posts nothing itself."),
            ("Radar", "Trends", "Scans for broad trends and new ideas."),
            ("Toolbox", "Tools", "Finds and tests new tools, and drops the ones that don’t help."),
        ],
    },
    "de": {
        "kicker": "Das Team", "title": "Wer macht was",
        "text": "Ein menschlicher Owner, ein Chief of Staff und zehn spezialisierte Agenten. Fahr über einen Agenten oder tippe ihn an, um seine Aufgabe zu sehen.",
        "trade": "Trading-Desk (Spielgeld)", "growth": "Wachstum & Produkte", "lead_grp": "Koordination", "human_grp": "Owner",
        "hint": "Die Linien zeigen, wer an den Chief of Staff berichtet.",
        "human": ("Desire", "Owner (Mensch)", "Setzt die Ziele und gibt alles frei, was echtes Geld, Käufe oder Deals betrifft."),
        "lead": ("Jojo", "Chief of Staff", "Plant den Tag, verteilt Aufgaben, prüft Ergebnisse und schreibt den Morgen- und Abendbericht."),
        "trade_agents": [
            ("Chef", "Desk-Manager", "Führt die Papier-Trading-Desks und schlägt Regeländerungen vor."),
            ("Scout", "Kandidaten-Scout", "Sucht neue Kandidaten für die Papier-Desks."),
            ("News", "Nachrichten", "Verfolgt Nachrichten, die für die Desks wichtig sein könnten."),
            ("Charts", "Chart-Leser", "Liest Kurscharts und Marktstruktur."),
            ("Skeptiker", "Der Skeptiker", "Hält dagegen, bevor etwas live geht, und sucht die Schwachstelle."),
        ],
        "growth_agents": [
            ("Publisher", "Content & Community", "Entwirft Posts und Antworten für X, Reddit und den Newsletter."),
            ("Produkte", "Gumroad & Vorlagen", "Baut und pflegt die Gumroad-Produkte und Vorlagen."),
            ("Analyst", "Social-Analyst", "Wertet Post-Performance und Nischendaten aus und liefert Ideen. Postet selbst nichts."),
            ("Radar", "Trends", "Sucht breite Trends und neue Ideen."),
            ("Toolbox", "Werkzeuge", "Findet und testet neue Tools und verwirft die, die nicht helfen."),
        ],
    },
}

FAQ = {
    "en": {
        "kicker": "FAQ", "title": "Fair questions",
        "items": [
            ("Why publish €0 in revenue?", "Because it is the real number. Build in public only means something if the zeros are shown too. We update the figures as they change."),
            ("What is paper trading?", "The trading desks use simulated money to test rules. The results are not income, not a product and not financial advice. We publish them because they are part of the system."),
            ("Are the n8n templates really free?", "Yes. You download the workflow.json, import it into your own n8n and add your own credentials. The files only contain placeholders."),
            ("Do you use AI to write this?", "Yes. The agents draft most of the work and a human owner approves anything involving money. We say so wherever a platform asks for it."),
            ("Does this site track me?", "No. There are no cookies, analytics or third-party requests. The theme toggle saves your choice in your own browser only."),
        ],
    },
    "de": {
        "kicker": "FAQ", "title": "Berechtigte Fragen",
        "items": [
            ("Warum zeigt ihr 0 € Ertrag?", "Weil es die echte Zahl ist. Build in Public bedeutet nur etwas, wenn auch die Nullen sichtbar sind. Wir aktualisieren die Zahlen, wenn sie sich ändern."),
            ("Was ist Papier-Trading?", "Die Trading-Desks testen Regeln mit Spielgeld. Die Ergebnisse sind kein Einkommen, kein Produkt und keine Finanzberatung. Wir zeigen sie, weil sie Teil des Systems sind."),
            ("Sind die n8n-Vorlagen wirklich kostenlos?", "Ja. Du lädst die workflow.json herunter, importierst sie in dein eigenes n8n und trägst deine eigenen Zugangsdaten ein. Die Dateien enthalten nur Platzhalter."),
            ("Schreibt ihr das mit KI?", "Ja. Die Agenten entwerfen den Großteil der Arbeit, und ein menschlicher Owner gibt alles frei, was Geld betrifft. Wo eine Plattform es verlangt, legen wir das offen."),
            ("Trackt mich diese Seite?", "Nein. Es gibt keine Cookies, keine Analytics und keine Anfragen an Dritte. Der Design-Schalter speichert deine Wahl nur in deinem eigenen Browser."),
        ],
    },
}


def _agent_btn(name, role, desc, group, cls="", aid=None):
    return (
        f'<button type="button" class="agent {cls}" aria-pressed="false" data-id="{esc(aid or name)}" '
        f'data-name="{esc(name)} · {esc(role)}" data-role="{esc(desc)}" data-group="{esc(group)}">'
        f'<span class="av" aria-hidden="true">{esc(name[:2])}</span><span>{esc(name)}<small>{esc(role)}</small></span></button>'
    )


def team_section(lang: str) -> str:
    t = TEAM[lang]
    trade = "".join(_agent_btn(n, r, d, t["trade"], "grp-trade") for n, r, d in t["trade_agents"])
    growth = "".join(_agent_btn(n, r, d, t["growth"]) for n, r, d in t["growth_agents"])
    hn, hr, hd = t["human"]
    ln, lr, ld = t["lead"]
    return f"""
      <section class="section" id="team">
        <div class="section-head">
          <div>
            <p class="kicker">{esc(t["kicker"])}</p>
            <h2>{esc(t["title"])}</h2>
            <p>{esc(t["text"])}</p>
          </div>
        </div>
        <div class="team">
          <svg class="team-lines" aria-hidden="true"></svg>
          <div class="team-col"><h3>{esc(t["trade"])}</h3>{trade}</div>
          <div class="team-center">
            {_agent_btn(hn, hr, hd, t["human_grp"], "is-lead is-human", "desire")}
            {_agent_btn(ln, lr, ld, t["lead_grp"], "is-lead")}
            <div class="team-detail" aria-live="polite"><div class="grp">{esc(t["lead_grp"])}</div><div class="who">{esc(ln)} · {esc(lr)}</div><p>{esc(ld)}</p></div>
            <p class="team-hint">{esc(t["hint"])}</p>
          </div>
          <div class="team-col"><h3>{esc(t["growth"])}</h3>{growth}</div>
        </div>
      </section>
"""


def faq_section(lang: str) -> str:
    t = FAQ[lang]
    items = "".join(
        f'<details><summary>{esc(q)}</summary><div class="faq-a"><p>{esc(a)}</p></div></details>'
        for q, a in t["items"]
    )
    return f"""
      <section class="section" id="faq">
        <div class="section-head"><div><p class="kicker">{esc(t["kicker"])}</p><h2>{esc(t["title"])}</h2></div></div>
        <div class="faq">{items}</div>
      </section>
"""


PROCESS = {
    "en": {"kicker": "How we work", "title": "From idea to public numbers",
           "text": "The same loop runs every day. Nothing that costs real money skips the human step.",
           "steps": [
               ("01", "Plan", "Jojo, the chief of staff, sets the day's priorities from yesterday's results and hands out work."),
               ("02", "Build", "Specialist agents draft the work: posts, products, templates, research, paper trades."),
               ("03", "Check", "Results are reviewed before they ship. Money, purchases and deals need the owner’s explicit OK."),
               ("04", "Publish & measure", "What ships goes live, and the numbers, including the zeros, go into the reports and onto this site."),
           ]},
    "de": {"kicker": "So arbeiten wir", "title": "Von der Idee zur öffentlichen Zahl",
           "text": "Jeden Tag läuft dieselbe Schleife. Nichts, was echtes Geld kostet, überspringt den menschlichen Schritt.",
           "steps": [
               ("01", "Planen", "Jojo, der Chief of Staff, setzt die Prioritäten des Tages anhand der Ergebnisse von gestern und verteilt die Arbeit."),
               ("02", "Bauen", "Spezialisierte Agenten entwerfen die Arbeit: Posts, Produkte, Vorlagen, Recherche, Papier-Trades."),
               ("03", "Prüfen", "Ergebnisse werden geprüft, bevor sie live gehen. Geld, Käufe und Deals brauchen das ausdrückliche OK des Owners."),
               ("04", "Veröffentlichen & messen", "Was fertig ist, geht live, und die Zahlen, auch die Nullen, landen in den Berichten und auf dieser Seite."),
           ]},
}

STACK = {
    "en": {"kicker": "Built with", "title": "A small, boring stack", "text": "Static files, no trackers, no build server. These are the tools the system actually runs on."},
    "de": {"kicker": "Gebaut mit", "title": "Ein kleiner, solider Stack", "text": "Statische Dateien, keine Tracker, kein Build-Server. Das sind die Werkzeuge, auf denen das System wirklich läuft."},
    "items": [
        ("Python", "build.py, desks, reports", '<path d="M12 3c-4 0-4 1.7-4 1.7V7h4v1H6.3S3 7.6 3 12s2.9 4.2 2.9 4.2H8v-2.1s-.1-2.9 2.8-2.9h3.8s2.7 0 2.7-2.6V4.9S17.7 3 12 3Zm-2 1.4a.8.8 0 1 1 0 1.6.8.8 0 0 1 0-1.6Z"/><path d="M12 21c4 0 4-1.7 4-1.7V17h-4v-1h5.7s3.3.4 3.3-4-2.9-4.2-2.9-4.2H16v2.1s.1 2.9-2.8 2.9H9.4s-2.7 0-2.7 2.6v3.7S6.3 21 12 21Zm2-1.4a.8.8 0 1 1 0-1.6.8.8 0 0 1 0 1.6Z" opacity=".6"/>'),
        ("GitHub Pages", "Hosting, HTTPS", '<path d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.7c-2.8.6-3.4-1.3-3.4-1.3-.4-1.2-1.1-1.5-1.1-1.5-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.6 2.4 1.1 3 .9.1-.7.4-1.1.6-1.4-2.2-.3-4.6-1.1-4.6-5 0-1.1.4-2 1-2.7-.1-.3-.4-1.3.1-2.7 0 0 .8-.3 2.8 1a9.6 9.6 0 0 1 5 0c1.9-1.3 2.8-1 2.8-1 .5 1.4.2 2.4.1 2.7.6.7 1 1.6 1 2.7 0 3.9-2.3 4.7-4.6 4.9.4.3.7.9.7 1.9V21c0 .3.2.6.7.5A10 10 0 0 0 12 2Z"/>'),
        ("n8n", "Workflows, templates", '<circle cx="5" cy="12" r="2.6"/><circle cx="12" cy="7" r="2.6"/><circle cx="12" cy="17" r="2.6"/><circle cx="19" cy="12" r="2.6"/><path d="M7.3 11 9.8 8.3M7.3 13l2.5 2.7M14.2 8.3l2.5 2.7M14.2 15.7l2.5-2.7" stroke="currentColor" stroke-width="1.6" fill="none"/>'),
        ("Claude API", "Weekly analysis", '<path d="M12 2.5 13.9 9l6.6-1.2-5 4.4 3.6 5.7-6.1-2.7L12 21.5l-1-6.3-6.1 2.7 3.6-5.7-5-4.4L10.1 9 12 2.5Z"/>'),
        ("Gumroad", "Products", '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M15.5 9.5A4 4 0 1 0 16 13h-4"/>'),
        ("beehiiv", "Newsletter", '<rect x="3" y="5" width="18" height="14" rx="3" fill="none" stroke="currentColor" stroke-width="2"/><path d="m4 7 8 6 8-6" fill="none" stroke="currentColor" stroke-width="2"/>'),
    ],
}

CASE = {
    "en": {"kicker": "Case study", "title": "This website, rebuilt in one evening",
           "text": "Our own site is the first project. Same content, same honest numbers. New design system, motion, a team diagram and EN/DE, still static and tracker-free.",
           "before": "Before · 20 Nov 2026", "after": "After · 21 Nov 2026",
           "points": ["Self-hosted font, no third-party requests", "Light and dark theme, reduced-motion support", "Canonical, hreflang, Open Graph, sitemap and llms.txt", "Hosted on GitHub Pages: server cost for the site €0"],
           "alt_before": "Screenshot of the old Desire Agency home page: serif headings on a beige background", "alt_after": "Screenshot of the new Desire Agency home page: dark hero with the ledger card", "cta": "Want a site like this?"},
    "de": {"kicker": "Fallstudie", "title": "Diese Website, an einem Abend neu gebaut",
           "text": "Unsere eigene Seite ist das erste Projekt. Gleicher Inhalt, gleiche ehrliche Zahlen. Neues Design-System, Animationen, ein Team-Schaubild und EN/DE, weiterhin statisch und ohne Tracker.",
           "before": "Vorher · 20.11.2026", "after": "Nachher · 21.11.2026",
           "points": ["Schrift selbst gehostet, keine Anfragen an Dritte", "Helles und dunkles Design, Rücksicht auf reduzierte Bewegung", "Canonical, hreflang, Open Graph, Sitemap und llms.txt", "Gehostet auf GitHub Pages: Serverkosten für die Seite 0 €"],
           "alt_before": "Screenshot der alten Desire-Agency-Startseite: Serifen-Überschriften auf beigem Hintergrund", "alt_after": "Screenshot der neuen Desire-Agency-Startseite: dunkler Hero mit dem Kassenbuch", "cta": "Auch so eine Website?"},
}


def process_section(lang: str) -> str:
    t = PROCESS[lang]
    steps = "".join(
        f'<li class="step"><span class="step-n">{n}</span><h3>{esc(h)}</h3><p>{esc(p)}</p></li>' for n, h, p in t["steps"]
    )
    return f"""
      <section class="section" id="process">
        <div class="section-head"><div><p class="kicker">{esc(t["kicker"])}</p><h2>{esc(t["title"])}</h2><p>{esc(t["text"])}</p></div></div>
        <ol class="steps">{steps}</ol>
      </section>
"""


def stack_section(lang: str) -> str:
    t = STACK[lang]
    items = "".join(
        f'<li class="stack-item"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{svg}</svg><span><b>{esc(n)}</b><small>{esc(d)}</small></span></li>'
        for n, d, svg in STACK["items"]
    )
    return f"""
      <section class="section" id="stack">
        <div class="section-head"><div><p class="kicker">{esc(t["kicker"])}</p><h2>{esc(t["title"])}</h2><p>{esc(t["text"])}</p></div></div>
        <ul class="stack">{items}</ul>
      </section>
"""


def case_section(lang: str, paths: dict) -> str:
    t = CASE[lang]
    root = paths["css"][: -len("css/site.css")]
    pts = "".join(f"<li>{esc(x)}</li>" for x in t["points"])
    def frame(src, cap, alt, cls=""):
        return (f'<figure class="mock {cls}"><div class="mock-bar" aria-hidden="true"><i></i><i></i><i></i><span>maximussoroka.github.io</span></div>'
                f'<img src="{root}img/{src}" width="960" height="600" loading="lazy" decoding="async" alt="{esc(alt)}"><figcaption>{esc(cap)}</figcaption></figure>')
    return f"""
      <section class="section" id="case-study">
        <div class="section-head"><div><p class="kicker">{esc(t["kicker"])}</p><h2>{esc(t["title"])}</h2><p>{esc(t["text"])}</p></div></div>
        <div class="case">
          <div class="case-shots">
            {frame("case-before.svg", t["before"], t["alt_before"], "is-before")}
            {frame("case-after.svg", t["after"], t["alt_after"], "is-after")}
          </div>
          <div><ul class="checks">{pts}</ul>
          <p style="margin:1.2rem 0 0"><a class="btn btn-ghost" href="{paths["websites"]}">{esc(t["cta"])} <span class="arrow" aria-hidden="true">→</span></a></p></div>
        </div>
      </section>
"""


CONTACT_EMAIL = "desire.studio.agency@gmail.com"

WEBSITES = {
    "en": {
        "title": "Websites for small businesses — Desire Agency",
        "description": "Fast, mobile-first websites for small businesses, built by Desire Agency in Lisbon. Vitrine from €390, Atelier from €750, Maison from €1,190, Care €29/month (plus VAT). No builder subscription, no tracking unless you want it.",
        "kicker": "Websites", "h1": "Fast, honest websites for small businesses",
        "lede": "A clean site that works on the phone, brings enquiries and belongs to you. No builder subscription and no tracking unless you want it. Built by the same team that runs this site.",
        "status": "Projects start after a short call. You get a written quote first, then the invoice.",
        "vat": "Net prices plus 23% VAT.",
        "from": "from", "per_month": "/ month", "plus_vat": "+ VAT",
        "delivery": "Delivery", "revisions": "Revisions",
        "ask": "Ask about {name}", "subject": "Enquiry {name}",
        "common_title": "Included in every package",
        "common": ["Mobile-first, premium design in the style of this site", "One clear main action: WhatsApp, call or form", "Technical SEO: titles, descriptions, sitemap, robots.txt, preview image", "Basic legal pages; no tracking unless you ask for it", "Hosting on GitHub Pages with HTTPS in the first year; you own the files", "Domain set up in your name (registry fee paid by you or passed on 1:1)"],
        "packages": [
            ("Vitrine", "One-page site", "For a local business or a single offer.", ["One long page, one language (PT, EN or DE)", "WhatsApp button and/or contact form", "Basic SEO and preview image"], "390 €", False, "5–7 working days", "2 rounds"),
            ("Atelier", "Business site, 3–5 pages", "For businesses that need more than one page.", ["Everything in Vitrine", "Up to 5 pages, one language", "Navigation, 404 page, shared footer", "Optional embedded map and links to your profiles"], "750 €", False, "10–14 working days", "2 rounds"),
            ("Maison", "Up to 8 pages, two languages", "For international or tourist audiences.", ["Everything in Atelier", "Up to 8 pages, two languages with switcher", "SEO per language with hreflang"], "1,190 €", False, "14–21 working days", "3 rounds"),
            ("Care", "Monthly care (optional)", "Keeps the site running after launch. Cancel with 30 days’ notice.", ["Hosting and HTTPS", "Uptime check and a heads-up if the site goes down", "Backups via Git history", "Small content changes, up to 30 minutes a month"], "29 €", True, "", ""),
        ],
        "time_note": "Delivery times count from the complete briefing (texts, photos, logo, access), not from the first message.",
        "not": "Not included: shops, booking systems, member areas, WordPress, logo design, photography, ad campaigns. Anything beyond the package is quoted before we start.",
        "example": "Live example: this website.",
        "contact": "Questions first? Write to us",
    },
    "de": {
        "title": "Websites für kleine Betriebe — Desire Agency",
        "description": "Schnelle, mobilfreundliche Websites für kleine Betriebe, gebaut von Desire Agency in Lissabon. Vitrine ab 390 €, Atelier ab 750 €, Maison ab 1.190 €, Care 29 €/Monat (zzgl. MwSt.). Kein Baukasten-Abo, kein Tracking, wenn du keines willst.",
        "kicker": "Websites", "h1": "Schnelle, ehrliche Websites für kleine Betriebe",
        "lede": "Eine klare Seite, die auf dem Handy funktioniert, Anfragen bringt und dir gehört. Kein Baukasten-Abo und kein Tracking, wenn du keines willst. Gebaut vom selben Team, das diese Seite betreibt.",
        "status": "Projektstart nach einem kurzen Gespräch. Du bekommst zuerst ein schriftliches Angebot, danach die Rechnung.",
        "vat": "Nettopreise zzgl. 23 % MwSt. (IVA).",
        "from": "ab", "per_month": "/ Monat", "plus_vat": "zzgl. MwSt.",
        "delivery": "Lieferzeit", "revisions": "Korrekturen",
        "ask": "{name} anfragen", "subject": "Anfrage {name}",
        "common_title": "In jedem Paket enthalten",
        "common": ["Hochwertiges, mobilfreundliches Design im Stil dieser Seite", "Eine klare Hauptaktion: WhatsApp, Anruf oder Formular", "Technisches SEO: Titel, Beschreibungen, Sitemap, robots.txt, Vorschaubild", "Rechtstexte in Grundform; kein Tracking, außer du wünschst es", "Hosting auf GitHub Pages mit HTTPS im ersten Jahr; die Dateien gehören dir", "Domain auf deinen Namen eingerichtet (Registry-Gebühr zahlst du oder sie wird 1:1 weitergegeben)"],
        "packages": [
            ("Vitrine", "Onepager", "Für einen lokalen Betrieb oder ein einzelnes Angebot.", ["Eine lange Seite, eine Sprache (PT, EN oder DE)", "WhatsApp-Button und/oder Kontaktformular", "Grundlegendes SEO und Vorschaubild"], "390 €", False, "5–7 Werktage", "2 Runden"),
            ("Atelier", "Firmenwebsite, 3–5 Seiten", "Für Betriebe, die mehr als eine Seite brauchen.", ["Alles aus Vitrine", "Bis zu 5 Seiten, eine Sprache", "Navigation, 404-Seite, einheitlicher Footer", "Optional eingebettete Karte und Links zu deinen Profilen"], "750 €", False, "10–14 Werktage", "2 Runden"),
            ("Maison", "Bis 8 Seiten, zwei Sprachen", "Für internationales oder touristisches Publikum.", ["Alles aus Atelier", "Bis zu 8 Seiten, zwei Sprachen mit Umschalter", "SEO je Sprache mit hreflang"], "1.190 €", False, "14–21 Werktage", "3 Runden"),
            ("Care", "Monatliche Betreuung (optional)", "Hält die Seite nach dem Start am Laufen. Kündbar mit 30 Tagen Vorlauf.", ["Hosting und HTTPS", "Erreichbarkeitsprüfung mit Hinweis, wenn die Seite ausfällt", "Sicherung über die Git-Historie", "Kleine Inhaltsänderungen, bis 30 Minuten pro Monat"], "29 €", True, "", ""),
        ],
        "time_note": "Lieferzeiten gelten ab vollständigem Briefing (Texte, Fotos, Logo, Zugänge), nicht ab der ersten Nachricht.",
        "not": "Nicht enthalten: Shops, Buchungssysteme, Mitgliederbereiche, WordPress, Logo-Design, Fotos, Werbekampagnen. Alles darüber hinaus bekommst du vorher als Angebot.",
        "example": "Live-Beispiel: diese Website.",
        "contact": "Erst Fragen? Schreib uns",
    },
}


def _mailto(subject: str) -> str:
    from urllib.parse import quote
    return f"mailto:{CONTACT_EMAIL}?subject={quote(subject)}"


def websites_body(lang: str) -> str:
    t = WEBSITES[lang]
    paths = page_paths(lang, 1 if lang == "en" else 2)
    cards = []
    for i, (name, sub, who, feats, price, monthly, delivery, revs) in enumerate(t["packages"]):
        fl = "".join(f"<li>{esc(f)}</li>" for f in feats)
        meta = ""
        if delivery:
            meta = (f'<dl class="pkg-meta"><div><dt>{esc(t["delivery"])}</dt><dd>{esc(delivery)}</dd></div>'
                    f'<div><dt>{esc(t["revisions"])}</dt><dd>{esc(revs)}</dd></div></dl>')
        pre = "" if monthly else f'<span class="price-from">{esc(t["from"])}</span>'
        post = f'<span class="price-sub">{esc(t["per_month"])} · {esc(t["plus_vat"])}</span>' if monthly else f'<span class="price-sub">{esc(t["plus_vat"])}</span>'
        btn = "btn btn-primary" if i == 1 else "btn btn-ghost"
        cards.append(f"""
          <article class="product pkg{" is-featured" if i == 1 else ""}">
            <span class="pill">{esc(sub)}</span>
            <h3>{esc(name)}</h3>
            <p>{esc(who)}</p>
            <div class="price-line">{pre}<span class="price-big">{esc(price)}</span>{post}</div>
            <ul class="checks checks-sm">{fl}</ul>
            {meta}
            <div class="actions"><a class="{btn}" href="{esc(_mailto(t["subject"].format(name=name)))}">{esc(t["ask"].format(name=name))} <span class="arrow" aria-hidden="true">→</span></a></div>
          </article>""")
    common = "".join(f"<li>{esc(c)}</li>" for c in t["common"])
    return f"""
      <header class="hero">
        <p class="kicker">{esc(t["kicker"])}</p>
        <h1 class="page-title">{esc(t["h1"])}</h1>
        <p class="lede">{esc(t["lede"])}</p>
        <p class="notice notice-info" role="note">{esc(t["status"])}</p>
      </header>
      <h2 class="visually-hidden">{"Pakete" if lang == "de" else "Packages"}</h2>
      <div class="products products-4">{''.join(cards)}
      </div>
      <p class="note">{esc(t["vat"])} {esc(t["time_note"])}</p>
      <section class="section">
        <div class="split">
          <div class="panel"><h3>{esc(t["common_title"])}</h3><ul class="checks">{common}</ul></div>
          <div class="panel"><p>{esc(t["not"])}</p><p><a href="{paths["home"]}#case-study">{esc(t["example"])}</a></p>
            <p><a class="btn btn-ghost" href="{esc(_mailto(t["subject"].format(name="Website")))}">{esc(t["contact"])} <span class="arrow" aria-hidden="true">→</span></a></p></div>
        </div>
      </section>
"""


def home_body(lang: str, paths: dict) -> str:
    t = HOME[lang]
    ledger = "\n".join(
        f'<div class="ledger-row"><span>{label}</span><b class="{cls}" data-count>{val}</b></div>'
        for label, val, cls in t["ledger"]
    )
    stats = "\n".join(
        f'<div class="stat"><div class="value" data-count>{esc(v)}</div><div class="label">{lab}</div><div class="sub">{sub}</div></div>'
        for v, lab, sub in t["stats"]
    )
    shipped = "\n".join(
        f'<div class="ledger-row" style="border-color:var(--line);color:var(--muted)"><span style="color:var(--ink-2)">{esc(txt)}</span><b style="color:var(--muted);font-size:.82rem">{esc(d)}</b></div>'
        for d, txt in t["shipped"]
    )
    rules = "\n".join(f"<li>{esc(r)}</li>" for r in t["rules"])
    cards = []
    for p in t["products"]:
        url = paths["templates"] if p["url"] == "@templates" else p["url"]
        ext = ' rel="noopener"' if url.startswith("http") else ""
        pill_cls = "pill" if p["featured"] else "pill pill-free"
        btn_cls = "btn btn-primary" if p["featured"] else "btn btn-ghost"
        cards.append(f"""
          <article class="product{" is-featured" if p["featured"] else ""}">
            <div class="product-icon">{ICON[p["icon"]]}</div>
            <span class="{pill_cls}">{esc(p["pill"])}</span>
            <h3>{esc(p["title"])}</h3>
            <p>{esc(p["text"])}</p>
            <div class="price-line"><span class="price-big">{esc(p["price"])}</span><span class="price-sub">{p["price_sub"]}</span></div>
            <div class="actions"><a class="{btn_cls}" href="{url}"{ext}>{esc(p["cta"])} <span class="arrow" aria-hidden="true">→</span></a></div>
          </article>""")
    facts = "\n".join(
        f'<article class="fact"><h3>{esc(h)}</h3><p>{esc(p)}</p></article>'
        for h, p in t["facts"]
    )
    return f"""
      <section class="home-hero">
        <div>
          <p class="eyebrow"><span class="dot" aria-hidden="true"></span>{esc(t["eyebrow"])}</p>
          <h1>{esc(t["h1_a"])} <span class="grad">{esc(t["h1_b"])}</span></h1>
          <p class="lede">{esc(t["lede"])}</p>
          <div class="actions">
            <a class="btn btn-light" href="{esc(SUBSCRIBE_URL)}" rel="noopener">{esc(t["cta_news"])} <span class="arrow" aria-hidden="true">→</span></a>
            <a class="btn btn-outline-light" href="{GUIDE_URL}" rel="noopener">{esc(t["cta_guide"])}</a>
          </div>
          <div class="hero-links">
            <a href="{paths["templates"]}">{esc(t["link_tpl"])}</a>
            <a href="{JOURNAL_URL}" rel="noopener">{esc(t["link_journal"])}</a>
            <a href="{paths["n8n"]}">{esc(t["link_n8n"])}</a>
          </div>
          <p class="hero-note">{esc(t["hero_note"])}</p>
        </div>
        <aside class="ledger" aria-label="{esc(t["ledger_title"])}">
          <div class="ledger-head"><strong>{esc(t["ledger_title"])}</strong><span>{esc(NUMBERS_AS_OF[lang])}</span></div>
          {ledger}
          <p class="ledger-foot">{esc(t["ledger_foot"])}</p>
        </aside>
      </section>

      <section class="section" id="build-in-public">
        <div class="section-head">
          <div>
            <p class="kicker">{esc(t["bip_kicker"])}</p>
            <h2>{esc(t["bip_title"])}</h2>
            <p>{esc(t["bip_text"])}</p>
          </div>
          <p class="note" style="margin:0">{esc(NUMBERS_AS_OF[lang])}</p>
        </div>
        <div class="stats">
          {stats}
        </div>
        <div class="split" style="margin-top:1.1rem">
          <div class="panel">
            <h3>{esc(t["shipped_title"])}</h3>
            {shipped}
          </div>
          <div class="panel">
            <h3>{esc(t["rules_title"])}</h3>
            <ul style="margin:.4rem 0 0;padding-left:1.15rem;color:var(--ink-2);line-height:1.9">{rules}</ul>
          </div>
        </div>
      </section>

{process_section(lang)}
{team_section(lang)}
      <section class="section" id="products">
        <div class="section-head">
          <div>
            <p class="kicker">{esc(t["prod_kicker"])}</p>
            <h2>{esc(t["prod_title"])}</h2>
            <p>{esc(t["prod_text"])}</p>
          </div>
        </div>
        <div class="products">{''.join(cards)}
        </div>
      </section>

{case_section(lang, paths)}
      <section class="section" id="n8n">
        <div class="section-head">
          <div>
            <p class="kicker">{esc(t["n8n_kicker"])}</p>
            <h2>{esc(t["n8n_title"])}</h2>
            <p>{esc(t["n8n_text"])}</p>
          </div>
          <div class="actions" style="margin:0">
            <a class="btn btn-ghost" href="{paths["n8n"]}">{esc(t["cta1"])}</a>
            <a class="btn btn-ad" data-aff="n8n" href="https://n8n.io/">{esc(t["cta_n8n"])}</a>
          </div>
        </div>
        <p class="kicker" style="margin-top:.4rem">{esc(t["facts_title"])}</p>
        <div class="facts">{facts}</div>
        <p class="aff-state" data-aff-state="n8n"></p>
        <div class="panel" style="margin-top:1.1rem;display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap">
          <div style="max-width:44rem">
            <h3>{esc(t["dir_title"])}</h3>
            <p>{esc(t["dir_text"])}</p>
          </div>
          <a class="btn btn-ghost" href="{paths["directory"]}">{esc(t["cta2"])} <span class="arrow" aria-hidden="true">→</span></a>
        </div>
        <p class="note">{esc(t["rev"])}</p>
      </section>

{stack_section(lang)}
{faq_section(lang)}
      <section class="section">
        <div class="cta-band">
          <div>
            <h2>{esc(t["news_title"])}</h2>
            <p>{esc(t["news_text"])}</p>
          </div>
          <div class="actions">
            <a class="btn btn-light" href="{esc(SUBSCRIBE_URL)}" rel="noopener">{esc(t["news_cta"])} <span class="arrow" aria-hidden="true">→</span></a>
          </div>
        </div>
      </section>
"""


ARTICLE = {
    "en": {
        "title": "Why we recommend n8n — honest, sourced",
        "description": "Why we recommend n8n for most self-hosting and execution-based workflows, and when Make can still be the more practical first step. Sources checked 18 November 2026.",
        "h1": "Why we recommend n8n — honestly, with sources",
        "intro": (
            "This article is an honest, sourced recommendation of n8n. There are no active affiliate links on this site at the moment; "
            "product buttons go to the official vendor pages. This page may contain affiliate links in the future; those will be labelled "
            "<strong>#ad / Anzeige</strong>. There is no earnings promise and no revenue of our own (so far €0). "
            "Not financial advice, not a trading product."
        ),
        "context": "It is about tools that connect recurring workflows between apps, or that build agent workflows.",
        "s1": "The recommendation in one sentence",
        "p1": (
            "<strong>For most cases that matter in this project — being able to self-host, choosing where data lives, "
            "and paying for complete workflow runs rather than every step — we recommend n8n.</strong> "
            "Make remains a serious alternative if you want to start without your own server and prefer a credits model with a free plan. "
            "A blanket claim that “n8n is always cheaper” is not substantiated."
        ),
        "s2": "Why n8n",
        "why": [
            (
                "<strong>Pricing model:</strong> In the cloud, n8n bills by monthly workflow executions, regardless of complexity. "
                "A run counts as one execution even if the workflow has many steps. According to the pricing page (billed annually): "
                "Starter €20/month, Pro €50/month, Business €667/month, Enterprise on request. All plans include, according to the vendor, "
                "unlimited users, workflows and integrations. Monthly billing exists according to the documentation and is more expensive; "
                "the monthly amounts were not stated as figures on the public pricing page, so they are not stated here either."
            ),
            (
                "<strong>Self-hosting:</strong> The Community Edition for self-hosting is free on GitHub. Paid Business/Enterprise options "
                "also exist with self-hosting. If you run the server yourself, you decide where the data lives."
            ),
            (
                "<strong>Cloud data location:</strong> For hosted cloud plans, n8n names Frankfurt (EU) as the storage location."
            ),
            (
                "<strong>Trial:</strong> 14 days, according to n8n, without a credit card on the pricing page."
            ),
        ],
        "why_end": "That fits the typical decision in this project better than a purely hosted credits model.",
        "s3": "Where Make can honestly be a better fit",
        "make": (
            "Make is a hosted, visual platform and bills in credits per action. Most actions use 1 credit, some AI features use more. "
            "Unused credits expire at the end of the period. If you run out of credits, scenarios stop until credits are available again."
        ),
        "make2": (
            "On the free plan, Make states 1,000 credits per month. Prices for paid plans were not reliably readable when the official "
            "pricing page was retrieved; they are therefore not listed here."
        ),
        "make3": (
            "<strong>If you want to start quickly without your own server</strong> and need a free entry allowance, Make can be the more practical first step. "
            "Whether Make or n8n is cheaper for the same flow depends on how many steps a flow has and how often it runs. "
            "That cannot be predicted in euros in general."
        ),
        "s4": "What this recommendation is not",
        "not_list": [
            "Not evidence that an affiliate link or a subscription will pay off for you.",
            "Not “always n8n, never Make”.",
            "Not a comparison of the user interface as a taste judgement without a source.",
        ],
        "s5": "Affiliate programmes — for context only, not an earnings promise",
        "aff_intro": "Both vendors have an official partner programme. The rates below are the vendors’ figures, not our own revenue.",
        "th": ("", "n8n", "Make"),
        "rows": [
            ("Commission", "30% of net cloud revenue", "35% of subscription payments"),
            (
                "Duration",
                "12 months",
                "12 months (one FAQ on the same page says 24 months; that contradiction remains)",
            ),
            (
                "Payout",
                "PayPal, monthly, from €100",
                "Wise, from 3 paying users and $100, 2–3 weeks after a request",
            ),
            (
                "Particulars",
                "Cloud referrals only; net basis, because customers pay including tax",
                "No retroactive attribution without a link; the “Make” brand in ads only with written consent",
            ),
        ],
        "aff_note": (
            "If this article later appears with partner links, the links belong here and stay labelled <strong>#ad / Anzeige</strong>."
        ),
        "see_n8n": "See n8n",
        "see_make": "See Make",
        "passive": (
            "Make advertises its programme page with “passive income”. That is a marketing phrase, not evidence that money arrives without ongoing work. "
            "Our own revenue from this: so far €0."
        ),
        "s6": "A practical start (no account is created for you here)",
        "steps": [
            "Write down your own flow in steps (trigger, how often, which apps, whether data should stay in the EU).",
            "Think through the same flow once as an n8n execution and once as a Make credit chain.",
            "Check the current official pricing pages; figures in this article apply to 18 November 2026 and can change.",
            "Only then create an account — that is your decision, not part of this article. If you follow our recommendation, start with n8n (cloud or Community Edition).",
        ],
        "s7": "Sources",
        "sources_note": "Full table and open points are documented in the internal source pack (programme table and sources file, 18 November 2026).",
    },
    "de": {
        "title": "Warum wir n8n empfehlen — ehrlich, mit Quellen",
        "description": "Warum wir n8n für die meisten Fälle mit Selbst-Hosting und Abrechnung nach Workflow-Läufen empfehlen, und wann Make der praktischere erste Schritt sein kann. Quellenstand 18.11.2026.",
        "h1": "Warum wir n8n empfehlen — ehrlich, mit Quellen",
        "intro": (
            "Dieser Text ist eine ehrliche, quellenbelegte Empfehlung für n8n. Auf dieser Seite sind derzeit keine Affiliate-Links aktiv; "
            "die Produkt-Buttons führen auf die offiziellen Anbieterseiten. Diese Seite kann in Zukunft Affiliate-Links enthalten; "
            "diese werden als <strong>#ad / Anzeige</strong> gekennzeichnet. Es gibt kein Gewinnversprechen und keinen eigenen Umsatz (bisher 0 €). "
            "Keine Finanzberatung, kein Trading-Produkt."
        ),
        "context": "Es geht um Werkzeuge, mit denen man wiederkehrende Abläufe zwischen Apps verbindet oder Agenten-Workflows baut.",
        "s1": "Empfehlung in einem Satz",
        "p1": (
            "<strong>Für die meisten Fälle, die in diesem Projekt zählen — selbst hosten können, Datenort festlegen, "
            "nach ganzen Workflow-Läufen statt nach jedem Schritt zahlen — empfehlen wir n8n.</strong> "
            "Make bleibt eine seriöse Alternative, wenn ihr ohne eigenen Server starten und ein Credits-Modell mit Free-Plan wollt. "
            "Eine pauschale Aussage „n8n ist immer günstiger“ ist nicht belegt."
        ),
        "s2": "Warum n8n",
        "why": [
            (
                "<strong>Preismodell:</strong> n8n berechnet in der Cloud nach monatlichen Workflow-Executions, unabhängig von der Komplexität. "
                "Ein Lauf zählt als eine Execution, auch wenn der Workflow viele Schritte hat. Laut Preisseite (jährlich abgerechnet): "
                "Starter 20 €/Monat, Pro 50 €/Monat, Business 667 €/Monat, Enterprise auf Anfrage. Alle Pläne enthalten laut Anbieter "
                "unbegrenzt Nutzer, Workflows und Integrationen. Monatliche Abrechnung gibt es laut Dokumentation und ist teurer; "
                "die monatlichen Beträge standen auf der öffentlichen Preisseite nicht als Zahl und stehen deshalb auch hier nicht."
            ),
            (
                "<strong>Self-Hosting:</strong> Die Community Edition zum Selbst-Hosten ist kostenlos auf GitHub. Bezahlte Business-/Enterprise-Optionen "
                "gibt es ebenfalls mit Self-Hosting. Wer den Server selbst betreibt, legt den Datenort selbst fest."
            ),
            (
                "<strong>Cloud-Datenort:</strong> Für die gehosteten Cloud-Pläne nennt n8n Frankfurt (EU) als Speicherort."
            ),
            (
                "<strong>Test:</strong> 14 Tage, laut n8n ohne Kreditkarte auf der Preisseite."
            ),
        ],
        "why_end": "Das trifft die typische Entscheidung in diesem Projekt besser als ein rein gehostetes Credits-Modell.",
        "s3": "Wo Make ehrlicherweise besser passen kann",
        "make": (
            "Make ist eine gehostete, visuelle Plattform und rechnet in Credits je Aktion. Die meisten Aktionen verbrauchen 1 Credit, einige KI-Funktionen mehr. "
            "Unbenutzte Credits verfallen zum Periodenende. Wer keine Credits mehr hat, dessen Szenarien laufen nicht weiter, bis wieder Credits da sind."
        ),
        "make2": (
            "Im Free-Plan nennt Make 1.000 Credits pro Monat. Die Preise der Bezahlpläne waren beim Abruf der offiziellen Preisseite nicht zuverlässig ablesbar; "
            "sie stehen deshalb hier nicht."
        ),
        "make3": (
            "<strong>Wenn ihr schnell ohne eigenen Server starten wollt</strong> und ein kostenloses Einstiegskontingent braucht, kann Make der praktischere erste Schritt sein. "
            "Ob Make oder n8n für denselben Ablauf günstiger ist, hängt davon ab, wie viele Schritte ein Ablauf hat und wie oft er läuft. "
            "Das lässt sich nicht allgemein in Euro vorhersagen."
        ),
        "s4": "Was diese Empfehlung nicht ist",
        "not_list": [
            "Kein Beleg, dass sich ein Affiliate-Link oder ein Abo für euch rechnet.",
            "Kein „immer n8n, nie Make“.",
            "Kein Vergleich der Benutzeroberfläche als Geschmacksurteil ohne Quelle.",
        ],
        "s5": "Affiliate-Programme — nur zur Einordnung, kein Verdienstversprechen",
        "aff_intro": "Beide Anbieter haben ein offizielles Partnerprogramm. Die Sätze unten sind die der Anbieter, kein eigener Umsatz.",
        "th": ("", "n8n", "Make"),
        "rows": [
            ("Provision", "30 % der Netto-Cloud-Einnahmen", "35 % der Abo-Zahlungen"),
            (
                "Dauer",
                "12 Monate",
                "12 Monate (eine FAQ auf derselben Seite nennt 24 Monate, das bleibt ein Widerspruch)",
            ),
            (
                "Auszahlung",
                "PayPal, monatlich, ab 100 €",
                "Wise, ab 3 zahlenden Nutzerinnen oder Nutzern und 100 $, 2–3 Wochen nach Anforderung",
            ),
            (
                "Besonderheit",
                "Nur Cloud-Empfehlungen; Nettobasis, weil Kundinnen und Kunden inklusive Steuern zahlen",
                "Keine nachträgliche Zuordnung ohne Link; Marke „Make“ in Anzeigen nur mit schriftlicher Zustimmung",
            ),
        ],
        "aff_note": (
            "Wenn dieser Text später mit Partnerschaftslinks erscheint, gehören die Links hierher und bleiben als <strong>#ad / Anzeige</strong> gekennzeichnet."
        ),
        "see_n8n": "n8n ansehen",
        "see_make": "Make ansehen",
        "passive": (
            "Make wirbt auf der Programmseite mit „passive income“. Das ist eine Werbeformel, kein Beleg dafür, dass ohne laufende Arbeit Geld fließt. "
            "Unser eigener Ertrag daraus: bisher 0 €."
        ),
        "s6": "Praktischer Einstieg (ohne Kontozwang in diesem Text)",
        "steps": [
            "Den eigenen Ablauf in Schritten aufschreiben (Auslöser, wie oft, welche Apps, ob Daten die EU nicht verlassen sollen).",
            "Denselben Ablauf einmal als n8n-Execution und einmal als Make-Credit-Kette denken.",
            "Die aktuellen offiziellen Preisseiten prüfen; Angaben in diesem Text gelten für den 18.11.2026 und können sich ändern.",
            "Erst danach ein Konto anlegen — das ist eure Entscheidung, nicht Teil dieses Textes. Wer unserer Empfehlung folgt, beginnt bei n8n (Cloud oder Community Edition).",
        ],
        "s7": "Quellen",
        "sources_note": "Ausführliche Tabelle und offene Punkte liegen im internen Quellenpaket (Programmtabelle und Quellendatei, 18.11.2026).",
    },
}

SOURCES = [
    ("https://n8n.io/affiliates/", "n8n.io/affiliates"),
    ("https://n8n.io/pricing/", "n8n.io/pricing"),
    ("https://docs.n8n.io/deploy/use-n8n-cloud/start-your-free-trial", "n8n Cloud trial docs"),
    ("https://www.make.com/affiliate/", "make.com/affiliate"),
    ("https://www.make.com/en/pricing", "make.com/en/pricing"),
]


def article_body(lang: str) -> str:
    t = ARTICLE[lang]
    why = "".join(f"<li>{item}</li>" for item in t["why"])
    nots = "".join(f"<li>{esc(item)}</li>" for item in t["not_list"])
    steps = "".join(f"<li>{esc(item)}</li>" for item in t["steps"])
    rows = "".join(
        f"<tr><th>{esc(a)}</th><td>{esc(b)}</td><td>{esc(c)}</td></tr>" for a, b, c in t["rows"]
    )
    src = "".join(f'<li><a href="{esc(u)}" rel="noopener noreferrer">{esc(l)}</a></li>' for u, l in SOURCES)
    return f"""
      <article>
        <h1>{esc(t["h1"])}</h1>
        <p>{t["intro"]}</p>
        <p>{esc(t["context"])}</p>
        <h2>{esc(t["s1"])}</h2>
        <p>{t["p1"]}</p>
        <h2>{esc(t["s2"])}</h2>
        <ul>{why}</ul>
        <p>{esc(t["why_end"])}</p>
        <h2>{esc(t["s3"])}</h2>
        <p>{esc(t["make"])}</p>
        <p>{esc(t["make2"])}</p>
        <p>{t["make3"]}</p>
        <h2>{esc(t["s4"])}</h2>
        <ul>{nots}</ul>
        <h2>{esc(t["s5"])}</h2>
        <p>{esc(t["aff_intro"])}</p>
        <div class="table-wrap">
          <table>
            <thead><tr><th>{esc(t["th"][0]) or ("Field" if lang == "en" else "Feld")}</th><th>{esc(t["th"][1])}</th><th>{esc(t["th"][2])}</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
        <p>{t["aff_note"]}</p>
        <div class="actions">
          <a class="btn btn-ad" data-aff="n8n" href="https://n8n.io/">{esc(t["see_n8n"])}</a>
          <a class="btn btn-ghost" data-aff="make" href="https://www.make.com/">{esc(t["see_make"])}</a>
        </div>
        <p class="aff-state" data-aff-state="n8n"></p>
        <p class="aff-state" data-aff-state="make"></p>
        <p>{esc(t["passive"])}</p>
        <h2>{esc(t["s6"])}</h2>
        <ol>{steps}</ol>
        <h2>{esc(t["s7"])}</h2>
        <ul>{src}</ul>
        <p class="note">{esc(t["sources_note"])}</p>
      </article>
"""


DIR = {
    "en": {
        "title": "Automation and AI-agent tools — sourced directory",
        "description": f"A sourced directory of {N_TOOLS} automation and AI-agent tools. Prices from official public pages dated {PRUEF_EN}.",
        "h1": "Directory of automation and AI-agent tools",
        "lede": (
            f"Sources checked on {PRUEF_EN}. {N_TOOLS} entries, n8n first. Our own revenue: €0. "
            "There are no active affiliate links at the moment. This page may contain affiliate links in the future; "
            "those will be labelled #ad / Anzeige. "
            "Where a figure was not reliably readable, it is marked unknown."
        ),
        "search": "Search tools",
        "all": "All",
        "automation": "Automation",
        "ai": "AI agents",
        "recommended": "Recommended",
        "price": "Price (official page)",
        "aff": "Affiliate",
        "yes": "Yes",
        "no": "Not substantiated",
        "official": "Official site",
        "pricing": "Pricing",
        "programme": "Programme page",
        "see": "See {name}",
        "empty": "No tools match this filter.",
        "note": "Prices can change. Check the official page before you buy. No earnings promises.",
        "machine": "A machine-readable copy of this directory is at /tools.json. A short site map for language models is at /llms.txt.",
    },
    "de": {
        "title": "Automatisierungs- und KI-Agenten-Tools — quellenbelegtes Verzeichnis",
        "description": f"Quellenbelegtes Verzeichnis mit {N_TOOLS} Automatisierungs- und KI-Agenten-Tools. Preise aus offiziellen öffentlichen Seiten vom {PRUEF}.",
        "h1": "Verzeichnis für Automatisierungs- und KI-Agenten-Tools",
        "lede": (
            f"Quellenstand: {PRUEF}. {N_TOOLS} Einträge, n8n zuerst. Eigener Ertrag: 0 €. "
            "Derzeit sind keine Affiliate-Links aktiv. Diese Seite kann in Zukunft Affiliate-Links enthalten; "
            "diese werden als #ad / Anzeige gekennzeichnet. "
            "Wo ein Betrag nicht zuverlässig ablesbar war, steht unbekannt."
        ),
        "search": "Tools durchsuchen",
        "all": "Alle",
        "automation": "Automatisierung",
        "ai": "KI-Agenten",
        "recommended": "Empfehlung",
        "price": "Preis (offizielle Seite)",
        "aff": "Affiliate",
        "yes": "Ja",
        "no": "Nicht belegt",
        "official": "Offizielle Seite",
        "pricing": "Preise",
        "programme": "Programmseite",
        "see": "{name} ansehen",
        "empty": "Kein Eintrag passt zu diesem Filter.",
        "note": "Preise können sich ändern. Vor einem Kauf die offizielle Seite prüfen. Kein Gewinnversprechen.",
        "machine": "Eine maschinenlesbare Fassung dieses Verzeichnisses liegt unter /tools.json. Eine kurze Seitenübersicht für Sprachmodelle liegt unter /llms.txt.",
    },
}


def directory_body(lang: str) -> str:
    t = DIR[lang]
    cards = []
    for i, raw in enumerate(TOOLS["tools"], 1):
        item = tool_view(raw, lang)
        featured = item["id"] == "n8n"
        group = group_of(item)
        search = " ".join(
            [
                item["name"],
                item["kategorie"],
                item["kurz"],
                item["preis"],
                item.get("affiliate_detail") or "",
            ]
        )
        st_cls = status_class(item.get("preis_status") or "")
        aff = item.get("affiliate") is True
        aff_label = t["yes"] if aff else t["no"]
        rec = (
            f'<span class="badge badge-rec">{esc(t["recommended"])}</span>'
            if featured
            else ""
        )
        links = [
            f'<a href="{esc(item["url"])}" rel="noopener noreferrer">{esc(t["official"])}</a>',
            f'<a href="{esc(item["preis_quelle"])}" rel="noopener noreferrer">{esc(t["pricing"])}</a>',
        ]
        if item.get("affiliate_quelle"):
            links.append(
                f'<a href="{esc(item["affiliate_quelle"])}" rel="noopener noreferrer">{esc(t["programme"])}</a>'
            )
        if item["id"] in ("n8n", "make"):
            label = t["see"].format(name=item["name"])
            links.insert(
                0,
                f'<a class="btn btn-ad" data-aff="{esc(item["id"])}" href="{esc(item["url"])}">{esc(label)}</a>',
            )
        state = (
            f'<p class="aff-state" data-aff-state="{esc(item["id"])}"></p>'
            if item["id"] in ("n8n", "make")
            else ""
        )
        cards.append(
            f"""
        <article class="card{" featured" if featured else ""}" id="{esc(item["id"])}" data-group="{esc(group)}" data-search="{esc(search)}">
          <div class="card-top">
            <div>
              <h2>{esc(item["name"])}</h2>
              <div class="cat">{esc(item["kategorie"])}</div>
            </div>
            <div>{rec}<span class="badge {st_cls}">{esc(item["preis_status"])}</span></div>
          </div>
          <p>{esc(item["kurz"])}</p>
          <p class="price"><strong>{esc(t["price"])}:</strong> {esc(item["preis"])}</p>
          <p class="aff-detail"><strong>{esc(t["aff"])}:</strong> {esc(aff_label)}. {esc(item.get("affiliate_detail") or "")}</p>
          {state}
          <p class="card-links">{" ".join(links)}</p>
        </article>"""
        )
    return f"""
      <header class="hero">
        <h1 class="page-title">{esc(t["h1"])}</h1>
        <p class="lede">{esc(t["lede"])}</p>
      </header>
      <div class="toolbar">
        <label class="visually-hidden" for="tool-search" style="position:absolute;left:-9999px">{esc(t["search"])}</label>
        <input class="search" id="tool-search" type="search" placeholder="{esc(t["search"])}" autocomplete="off">
        <div class="chips" role="group">
          <button type="button" class="chip" data-group="all" aria-pressed="true">{esc(t["all"])}</button>
          <button type="button" class="chip" data-group="automation" aria-pressed="false">{esc(t["automation"])}</button>
          <button type="button" class="chip" data-group="ai" aria-pressed="false">{esc(t["ai"])}</button>
        </div>
      </div>
      <div class="cards" id="tool-grid">
        {''.join(cards)}
      </div>
      <p class="empty" id="no-results">{esc(t["empty"])}</p>
      <p class="note">{esc(t["note"])}</p>
      <p class="note">{esc(t["machine"])}</p>
"""


LEGAL = {
    "en": {
        "title": "Legal notice / Impressum — Desire Agency",
        "description": "Legal notice and contact details for Desire Agency.",
        "h1": "Legal notice / Impressum",
        "lead": "Operator information for this website.",
        "fields": [
            ("Operator / responsible person", "Saveliy Soroka"),
            ("Address", "Av. Dom João II 36, 1998-017 Lisboa, Portugal"),
            ("Email / contact", "desire.studio.agency@gmail.com"),
            ("VAT ID, if required", "Not provided"),
        ],
        "status": (
            f"Published on 19 November 2026 without an n8n partner link "
            f"(N8N_AFFILIATE_URL in config.js is empty; buttons go to the official n8n site). "
            f"The n8n partner application was declined on 19 November 2026; a later reapplication is planned. "
            f"Source date for prices: {PRUEF_EN}. Own revenue: €0."
        ),
        "ad": (
            "Advertising: there are no active affiliate links on this site at the moment. "
            "This page may contain affiliate links in the future; those will be labelled #ad / Anzeige."
        ),
        "privacy": (
            "Privacy: this is a static website. We do not use cookies, tracking pixels or analytics, "
            "and we do not collect personal data through this site. The directory search runs only in your browser. "
            "Links to vendor sites lead directly to those providers."
        ),
    },
    "de": {
        "title": "Impressum / Kontakt — Desire Agency",
        "description": "Impressum und Kontaktdaten von Desire Agency.",
        "h1": "Impressum / Kontakt",
        "lead": "Anbieterinformationen für diese Website.",
        "fields": [
            ("Anbieter / verantwortliche Person", "Saveliy Soroka"),
            ("Anschrift", "Av. Dom João II 36, 1998-017 Lisboa, Portugal"),
            ("E-Mail / Kontakt", "desire.studio.agency@gmail.com"),
            ("USt-IdNr., falls erforderlich", "Nicht angegeben"),
        ],
        "status": (
            f"Veröffentlicht am 19.11.2026 ohne n8n-Partner-Link "
            f"(N8N_AFFILIATE_URL in config.js ist leer; die Buttons führen auf die offizielle n8n-Seite). "
            f"Die n8n-Partner-Bewerbung wurde am 19.11.2026 abgelehnt; eine spätere erneute Bewerbung ist geplant. "
            f"Quellenstand der Preise: {PRUEF}. Eigener Ertrag: 0 €."
        ),
        "ad": (
            "Werbung: Auf dieser Seite sind derzeit keine Affiliate-Links aktiv. "
            "Diese Seite kann in Zukunft Affiliate-Links enthalten; diese werden als #ad / Anzeige gekennzeichnet."
        ),
        "privacy": (
            "Datenschutz: Dies ist eine statische Website. Wir verwenden keine Cookies, Tracking-Pixel oder Analysedienste "
            "und erheben über diese Seite keine personenbezogenen Daten. Die Suche im Verzeichnis läuft nur in Ihrem Browser. "
            "Links zu Anbieterseiten führen unmittelbar dorthin."
        ),
    },
}


def _legal_field(k: str, v: str) -> str:
    if v.endswith("@gmail.com") or (v.count("@") == 1 and " " not in v):
        return f'<dt>{esc(k)}</dt><dd><a href="mailto:{esc(v)}">{esc(v)}</a></dd>'
    return f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>"


def legal_body(lang: str) -> str:
    t = LEGAL[lang]
    fields = "".join(_legal_field(k, v) for k, v in t["fields"])
    return f"""
      <div class="legal">
      <h1 class="page-title">{esc(t["h1"])}</h1>
      <p class="lede">{esc(t["lead"])}</p>
      <dl class="placeholder-box">{fields}</dl>
      <p>{esc(t["status"])}</p>
      <p>{esc(t["ad"])}</p>
      <h2>{"Privacy" if lang == "en" else "Datenschutz"}</h2>
      <p>{esc(t["privacy"])}</p>
      </div>
"""


TEMPLATES_PAGE = {
    "title": "Free n8n templates — Desire Agency",
    "description": "Three free n8n workflow templates: a daily RSS digest email, a form that writes to Google Sheets, and a website uptime alert. Credentials in the files are placeholders.",
}

TEMPLATES = [
    {
        "id": "rss-daily-digest-email",
        "title": "RSS to daily digest email",
        "summary": "Once a day (default 07:00 in the n8n instance timezone, set here to Europe/Lisbon), the workflow reads an RSS feed, builds an HTML list of up to 20 items, and emails the digest.",
        "file": "rss-daily-digest-email/workflow.json",
        "steps": [
            "In n8n: … → Import from File (or Add workflow → Import) and choose workflow.json.",
            "Open Read RSS feed and replace https://example.com/feed.xml with your feed URL. Use the same URL in the Code node if you want it printed in the email (feedUrl).",
            "In n8n, create an SMTP credential (your mailbox provider). Open Send digest email, remove the placeholder credential, and attach yours.",
            "Set From and To. Change the schedule in Every day at 07:00 if needed (the time follows the workflow timezone under Settings).",
            "Click Test workflow, confirm the email, then Activate. Leave it inactive until the test works.",
        ],
        "notes": [
            "The Code node escapes titles and links before building HTML.",
            "An empty feed still sends a short “no items” email so a silent failure is easier to notice.",
            "Required n8n nodes are built-in: Schedule Trigger, RSS Read, Code, Send Email.",
        ],
        "credentials": "SMTP account (placeholder)",
    },
    {
        "id": "form-to-google-sheet-notification",
        "title": "Form to Google Sheet and notification",
        "summary": "An n8n form collects Name, Email and Message. Each submission is appended to a Google Sheet, then a notification email is sent.",
        "file": "form-to-google-sheet-notification/workflow.json",
        "steps": [
            "In Google Sheets, create a spreadsheet with a tab named Submissions.",
            "In row 1, add the headers exactly: submitted_at, name, email, message.",
            "Copy the spreadsheet ID from the URL (https://docs.google.com/spreadsheets/d/<ID>/edit).",
            "In n8n: … → Import from File and choose workflow.json.",
            "Open Append to Google Sheet, replace PLACEHOLDER_SPREADSHEET_ID with your ID, and attach a Google Sheets OAuth2 credential you created in n8n (the Google account must have access to the spreadsheet).",
            "Create an SMTP credential, attach it to Send notification email, and set From and To.",
            "Open Contact form, save the workflow, and copy the form URL n8n shows. Submit a test entry. Check the sheet and the inbox, then Activate.",
        ],
        "notes": [
            "Form field labels (Name, Email, Message) must match the expressions in the Sheet and email nodes. Rename them in both places if you change the form.",
            "The form path slug is contact-form (under the Form Trigger options). Change it if you already use that path.",
            "Required n8n nodes are built-in: Form Trigger, Google Sheets, Send Email.",
        ],
        "credentials": "Google Sheets account (placeholder) and SMTP account (placeholder)",
    },
    {
        "id": "website-uptime-check-alert",
        "title": "Website uptime check to alert",
        "summary": "Every 5 minutes the workflow requests a URL. If the HTTP status is not 200, or no status is returned (timeout or network error), it waits 60 seconds and requests the URL again. An alert email is sent only if the second check also fails. A successful 200 on either check does not send mail.",
        "file": "website-uptime-check-alert/workflow.json",
        "steps": [
            "In n8n: … → Import from File and choose workflow.json.",
            "Open Request website and Retry request website and replace https://example.com/ with the URL to check in both nodes. Also replace that URL in the subject and body of Send down alert.",
            "Create an SMTP credential in n8n, attach it to Send down alert (remove the placeholder), and set From and To.",
            "The default retry wait is 60 seconds. To change it, open the Wait 60 seconds node and edit Amount and Unit.",
            "Optionally change the interval in Every 5 minutes, the 10-second timeout, or the If conditions if you want to accept other 2xx codes.",
            "Run a test against a URL you control (or temporarily point it at a path that returns 404) to see the wait and the alert, then point it at the real URL and Activate.",
        ],
        "notes": [
            "After the first failed check, the workflow waits 60 seconds and requests the URL again. The alert is sent only if that second check also fails (status other than 200, or a missing status).",
            "The HTTP nodes use “full response”, “never error”, and onError: continueRegularOutput, so a 4xx/5xx or a failed request can be evaluated instead of stopping the workflow.",
            "This is a simple local check, not a hosted monitoring service. It will not run while n8n is stopped, and it does not measure uptime percentages.",
            "Required n8n nodes are built-in: Schedule Trigger, HTTP Request, If, Wait, Send Email.",
        ],
        "credentials": "SMTP account (placeholder)",
    },
]


def templates_body() -> str:
    parts = [
        """
      <article>
        <h1>Three free n8n templates</h1>
        <p class="lede">Small starting points you can import into your own n8n, test, and only then turn on. They are free. The JSON files contain no real passwords, keys or accounts — only placeholders you replace with your own.</p>
        <p>In n8n, use <strong>… → Import from File</strong> and choose the <code>workflow.json</code> for the template you want. Follow the setup steps below. Leave the workflow inactive until a test run works.</p>
"""
    ]
    for t in TEMPLATES:
        steps = "\n".join(f"          <li>{esc(s)}</li>" for s in t["steps"])
        notes = "\n".join(f"          <li>{esc(n)}</li>" for n in t["notes"])
        parts.append(f"""
        <section class="section tpl-card" id="{esc(t['id'])}">
          <h2>{esc(t['title'])}</h2>
          <p>{esc(t['summary'])}</p>
          <div class="actions">
            <a class="btn btn-primary" href="{esc(t['file'])}" download>Download workflow.json</a>
            <button type="button" class="btn btn-ghost copy-btn" data-copy="{esc(t['file'])}">Copy file link</button>
          </div>
          <h3>Setup</h3>
          <ol>
{steps}
          </ol>
          <p class="note">Credentials in this file are placeholders: {esc(t['credentials'])}. Attach your own credentials in n8n before you activate the workflow.</p>
          <h3>Good to know</h3>
          <ul>
{notes}
          </ul>
        </section>
""")
    parts.append(f"""
        <section class="section">
          <h2>Get the build log</h2>
          <p>We write about what we actually build — including these templates — in the Desire Agency newsletter. No earnings promises. Our own revenue so far: €0.</p>
          <div class="actions">
            <a class="btn btn-primary" href="{esc(SUBSCRIBE_URL)}">{esc(SUBSCRIBE_LABEL['en'])}</a>
          </div>
        </section>
      </article>
""")
    return "".join(parts)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    print(f"wrote {path.relative_to(ROOT)}")


def not_found() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <title>Page not found — Desire Agency</title>
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="/css/site.css">
</head>
<body>
  <main class="wrap-narrow nf">
    <div class="code">404</div>
    <h1>Page not found</h1>
    <p class="lede" style="margin-left:auto;margin-right:auto">This URL is not part of the site. / Diese Adresse gehört nicht zur Seite.</p>
    <div class="actions" style="justify-content:center">
      <a class="btn btn-primary" href="/">Home (English)</a>
      <a class="btn btn-ghost" href="/de/">Start (Deutsch)</a>
    </div>
  </main>
</body>
</html>
"""


SITE_URL = "https://maximussoroka.github.io"


def site_url(path: str) -> str:
    return SITE_URL + (path if path.startswith("/") else "/" + path)


def directory_jsonld(lang: str) -> str:
    """schema.org ItemList of SoftwareApplication for the directory page."""
    t = DIR[lang]
    elements = []
    for i, raw in enumerate(TOOLS["tools"], 1):
        item = tool_view(raw, lang)
        app = {
            "@type": "SoftwareApplication",
            "name": item["name"],
            "url": item["url"],
            "description": item["kurz"],
            "applicationCategory": item["kategorie"],
            "operatingSystem": "Web",
        }
        # Price text is sourced prose, not a single number — do not invent amount/currency.
        if item.get("preis"):
            offer = {
                "@type": "Offer",
                "description": item["preis"],
                "url": item.get("preis_quelle") or item["url"],
            }
            app["offers"] = offer
        elements.append({"@type": "ListItem", "position": i, "item": app})
    payload = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": t["h1"],
        "description": t["description"],
        "numberOfItems": N_TOOLS,
        "url": site_url("/directory/" if lang == "en" else "/de/directory/"),
        "datePublished": "2026-11-19",
        "dateModified": "2026-11-19",
        "itemListElement": elements,
    }
    dumped = json.dumps(payload, ensure_ascii=False, indent=2).replace("</", "<\\/")
    alternate = site_url("/tools.json")
    return (
        f'  <link rel="alternate" type="application/json" href="{alternate}">\n'
        f'  <script type="application/ld+json">\n{dumped}\n  </script>\n'
    )


def public_tools_payload() -> dict:
    """Bilingual, public machine-readable directory. No affiliate links, no placeholder slots."""
    tools = []
    for raw in TOOLS["tools"]:
        en = tool_view(raw, "en")
        de = tool_view(raw, "de")
        entry = {
            "id": raw["id"],
            "name": raw["name"],
            "official_url": raw["url"],
            "pricing_url": raw["preis_quelle"],
            "recommended": raw["id"] == "n8n",
            "affiliate_link_on_this_site": False,
            "affiliate_programme_substantiated": raw.get("affiliate") is True,
            "en": {
                "category": en["kategorie"],
                "summary": en["kurz"],
                "price": en["preis"],
                "price_status": en["preis_status"],
                "affiliate_detail": en.get("affiliate_detail") or "",
            },
            "de": {
                "category": de["kategorie"],
                "summary": de["kurz"],
                "price": de["preis"],
                "price_status": de["preis_status"],
                "affiliate_detail": de.get("affiliate_detail") or "",
            },
        }
        if raw.get("affiliate_quelle"):
            entry["programme_url"] = raw["affiliate_quelle"]
        tools.append(entry)
    return {
        "name": "Desire Agency tool directory",
        "url": site_url("/directory/"),
        "url_de": site_url("/de/directory/"),
        "checked_on": TOOLS["pruefdatum"],
        "timezone": TOOLS["timezone_pruefung"],
        "own_revenue_eur": TOOLS["eigener_ertrag_eur"],
        "affiliate_links_active": False,
        "n_entries": N_TOOLS,
        "note": (
            "Prices come only from official public vendor pages on the checked date. "
            "Where a figure was not reliably readable, price_status is unknown or partial. "
            "There are no active affiliate links on this site. "
            "This is not financial advice. No earnings promises. Own revenue: €0."
        ),
        "note_de": (
            "Preise nur aus offiziellen öffentlichen Anbieterseiten vom Prüfdatum. "
            "Wo ein Betrag nicht zuverlässig ablesbar war, ist price_status unbekannt oder teilweise. "
            "Auf dieser Seite sind keine Affiliate-Links aktiv. "
            "Keine Finanzberatung. Kein Gewinnversprechen. Eigener Ertrag: 0 €."
        ),
        "pages": {
            "home_en": site_url("/"),
            "home_de": site_url("/de/"),
            "n8n_en": site_url("/n8n/"),
            "n8n_de": site_url("/de/n8n/"),
            "templates_en": site_url("/templates/"),
            "directory_en": site_url("/directory/"),
            "directory_de": site_url("/de/directory/"),
            "legal_en": site_url("/legal/"),
            "legal_de": site_url("/de/legal/"),
            "newsletter_subscribe": SUBSCRIBE_URL,
            "llms_txt": site_url("/llms.txt"),
            "tools_json": site_url("/tools.json"),
            "sitemap": site_url("/sitemap.xml"),
        },
        "n8n_templates": [
            {
                "id": t["id"],
                "title": t["title"],
                "summary": t["summary"],
                "page": site_url("/templates/") + "#" + t["id"],
                "download": site_url("/templates/" + t["file"]),
                "price": "free",
            }
            for t in TEMPLATES
        ],
        "tools": tools,
    }


def write_public_tools_json() -> None:
    payload = public_tools_payload()
    write(ROOT / "tools.json", json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_llms_txt() -> None:
    text_out = f"""# Desire Agency

> An honest, sourced recommendation of n8n, plus a directory of {N_TOOLS} automation and AI-agent tools. English is primary; German is under /de/.

Live site: {SITE_URL}/
Operator: Saveliy Soroka, Lisboa. Contact: desire.studio.agency@gmail.com (see /legal/).
Prices and programme terms: official public vendor pages, checked on {PRUEF_EN} ({TOOLS["timezone_pruefung"]}).
Own revenue so far: €0. No earnings promises. Not financial advice.
Products: Agent Team Guide ({GUIDE_URL}, $19), free Trading Journal + Risk Sheet ({JOURNAL_URL}).
Elsewhere: X {X_URL} · dev.to {DEVTO_URL} · Indie Hackers {IH_URL}.
There are no active affiliate links. Future affiliate links, if any, will be labelled #ad / Anzeige.
This is a static site with no cookies, tracking or analytics.

## Pages

- [Home (English)]({SITE_URL}/): Desire Agency, an AI agent team built in public from Lisbon. Real numbers including the zeros (revenue so far €0), products (Agent Team Guide, free trading journal, free n8n templates), why we recommend n8n, and sourced cloud-pricing facts as of {PRUEF_EN}.
- [Home (German)]({SITE_URL}/de/): The same start page in German.
- [n8n recommendation (English)]({SITE_URL}/n8n/): Sourced article on n8n, self-hosting, and a fair comparison with Make. Buttons go to the official n8n site; the n8n partner application was declined on 19 November 2026.
- [n8n recommendation (German)]({SITE_URL}/de/n8n/): The same article in German.
- [Tool directory (English)]({SITE_URL}/directory/): {N_TOOLS} sourced entries (n8n listed first). Each entry has a short description, official and pricing URLs, and a price field. Where a figure was not reliably readable, it is marked unknown. schema.org JSON-LD (ItemList of SoftwareApplication) is embedded in the page.
- [Tool directory (German)]({SITE_URL}/de/directory/): The same directory in German, with the same JSON-LD in German wording.
- [Free n8n templates (English)]({SITE_URL}/templates/): Three free, importable n8n workflows (RSS digest email, form to Google Sheet, website uptime alert with a 60-second retry before the alert). Each section has setup steps and a download link to workflow.json. Credentials in the files are placeholders only. There is no German version of this page.
- [Legal notice / Impressum (English)]({SITE_URL}/legal/): Operator, address, contact, advertising note, and privacy (static site, no cookies or tracking).
- [Legal notice / Impressum (German)]({SITE_URL}/de/legal/): The same legal notice in German.
- [Websites (English)]({SITE_URL}/websites/): Website service for small businesses: Vitrine (one page) from €390, Atelier (3–5 pages) from €750, Maison (up to 8 pages, two languages) from €1,190, Care €29/month. Net prices plus 23% VAT. Delivery times count from the complete briefing. Enquiries by email only; no online payment.
- [Websites (German)]({SITE_URL}/de/websites/): The same service page in German.
- [Desire Agency newsletter]({SUBSCRIBE_URL}): Sign-up page for the free “build log” newsletter. No earnings promises.

## Machine-readable

- [tools.json]({SITE_URL}/tools.json): JSON copy of all {N_TOOLS} directory entries in English and German, including official URLs, pricing URLs, sourced price text, and price-status. No affiliate links.
- [sitemap.xml]({SITE_URL}/sitemap.xml): URL list for this site.
- [robots.txt]({SITE_URL}/robots.txt): Allows indexing and points to the sitemap.

## Optional

- Do not invent prices or programme terms. If a field is unknown or partial, say so and send readers to the vendor's official page.
- Product buttons currently go to official vendor sites (https://n8n.io/, https://www.make.com/), not to affiliate URLs.
"""
    write(ROOT / "llms.txt", text_out)


def write_sitemap() -> None:
    paths = [
        ("/", "1.0", "weekly"),
        ("/n8n/", "0.9", "weekly"),
        ("/templates/", "0.8", "weekly"),
        ("/directory/", "0.9", "weekly"),
        ("/legal/", "0.6", "yearly"),
        ("/de/", "0.8", "weekly"),
        ("/de/n8n/", "0.7", "weekly"),
        ("/de/directory/", "0.7", "weekly"),
        ("/de/legal/", "0.5", "yearly"),
        ("/websites/", "0.9", "weekly"),
        ("/de/websites/", "0.8", "weekly"),
        ("/llms.txt", "0.5", "weekly"),
        ("/tools.json", "0.6", "weekly"),
    ]
    lastmod = "2026-11-21"
    urls = []
    for path, prio, freq in paths:
        urls.append(
            "  <url>\n"
            f"    <loc>{esc(site_url(path))}</loc>\n"
            f"    <lastmod>{lastmod}</lastmod>\n"
            f"    <changefreq>{freq}</changefreq>\n"
            f"    <priority>{prio}</priority>\n"
            "  </url>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    write(ROOT / "sitemap.xml", xml)


def write_robots() -> None:
    write(
        ROOT / "robots.txt",
        "User-agent: *\n"
        "Allow: /\n"
        f"\nSitemap: {site_url('/sitemap.xml')}\n",
    )


def build() -> None:
    pages = [
        (ROOT / "index.html", "en", "home", 0, HOME["en"], home_body),
        (ROOT / "n8n" / "index.html", "en", "n8n", 1, ARTICLE["en"], lambda lang, paths=None: article_body(lang)),
        (ROOT / "templates" / "index.html", "en", "templates", 1, TEMPLATES_PAGE, lambda lang, paths=None: templates_body()),
        (ROOT / "directory" / "index.html", "en", "directory", 1, DIR["en"], lambda lang, paths=None: directory_body(lang)),
        (ROOT / "legal" / "index.html", "en", "legal", 1, LEGAL["en"], lambda lang, paths=None: legal_body(lang)),
        (ROOT / "de" / "index.html", "de", "home", 1, HOME["de"], home_body),
        (ROOT / "de" / "n8n" / "index.html", "de", "n8n", 2, ARTICLE["de"], lambda lang, paths=None: article_body(lang)),
        (ROOT / "de" / "directory" / "index.html", "de", "directory", 2, DIR["de"], lambda lang, paths=None: directory_body(lang)),
        (ROOT / "de" / "legal" / "index.html", "de", "legal", 2, LEGAL["de"], lambda lang, paths=None: legal_body(lang)),
        (ROOT / "websites" / "index.html", "en", "websites", 1, WEBSITES["en"], lambda lang, paths=None: websites_body(lang)),
        (ROOT / "de" / "websites" / "index.html", "de", "websites", 2, WEBSITES["de"], lambda lang, paths=None: websites_body(lang)),
    ]
    for path, lang, page, depth, meta, body_fn in pages:
        paths = page_paths(lang, depth)
        if page == "home":
            body = body_fn(lang, paths)
        else:
            body = body_fn(lang)
        extra_head = directory_jsonld(lang) if page == "directory" else ""
        html_out = shell(lang, page, depth, meta["title"], meta["description"], body, extra_head=extra_head)
        write(path, html_out)
    write(ROOT / "404.html", not_found())
    write_public_tools_json()
    write_llms_txt()
    write_sitemap()
    write_robots()
    print(f"done. {N_TOOLS} tools, languages en+de, plus /templates/. Wrote llms.txt, tools.json, sitemap.xml, robots.txt.")


if __name__ == "__main__":
    build()
