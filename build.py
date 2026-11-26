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

def T3(lang: str, en: str, de: str, pt: str) -> str:
    return {"en": en, "de": de, "pt": pt}[lang]


NAV = {
    "pt": [
        ("home", "Início"),
        ("websites", "Sites"),
        ("n8n", "n8n (EN)"),
        ("templates", "Templates"),
        ("directory", "Diretório (EN)"),
        ("legal", "Aviso legal"),
    ],
    "en": [
        ("home", "Home"),
        ("websites", "Websites"),
        ("n8n", "Recommend n8n"),
        ("templates", "Templates"),
        ("directory", "Directory"),
        ("legal", "Legal notice"),
    ],
    "de": [
        ("home", "Start"),
        ("websites", "Websites"),
        ("n8n", "n8n-Empfehlung"),
        ("templates", "Templates"),
        ("directory", "Verzeichnis"),
        ("legal", "Impressum"),
    ],
}

SUBSCRIBE_URL = "https://desireagency.beehiiv.com/subscribe"
SUBSCRIBE_LABEL = {
    "en": "Get the build log",
    "de": "Build-Log abonnieren",
    "pt": "Receber o build log",
}

FOOT = {
    "en": (
        f"Prices and programme terms as of {PRUEF_EN}, from the vendors’ official pages. "
        "Not financial advice."
    ),
    "de": (
        f"Stand der Preise und Programmbedingungen: {PRUEF}, offizielle Seiten der Anbieter. "
        "Keine Finanzberatung."
    ),
    "pt": "Não é aconselhamento financeiro.",
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
    if lang == "pt":  # only /pt/websites/ exists; other pages link to English
        return {
            "home": "../../", "n8n": "../../n8n/", "templates": "../../templates/",
            "directory": "../../directory/", "websites": "../websites/", "legal": "../../legal/",
            "other_lang": "../../", "config": "../../config.js", "css": "../../css/site.css",
            "js_aff": "../../js/affiliate.js", "js_dir": "../../js/directory.js",
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
    if lang == "pt":
        return "../../"
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
GUIDE_EARLY_URL = GUIDE_URL + "/EARLYBIRD"

# The public site no longer publishes the cash ledger (revenue, sales, paper P&L).
# data/ledger.json and /workspace/website/tools/update_ledger.py are internal only.
# Do not wire those figures back into any generated page.

LOGO_SVG = (
    '<svg class="brand-mark" viewBox="0 0 120 120" aria-hidden="true" focusable="false">'
    '<defs><linearGradient id="ng" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff5ee6"/><stop offset=".5" stop-color="#b45cff"/><stop offset="1" stop-color="#3fe6f2"/></linearGradient></defs><rect width="120" height="120" rx="28" fill="#07071a"/><g transform="translate(11.4 12.2) scale(.8)"><path d="M22 16H58C83 16 100 35 100 60C100 85 83 104 58 104H22ZM40 34V86H57C71 86 81 75 81 60C81 45 71 34 57 34ZM22 16L40 34M22 104L40 86" fill="none" stroke="url(#ng)" stroke-width="10" stroke-linejoin="round" stroke-linecap="round"/></g>'
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
    ("pt", "websites"): "/pt/websites/",
}

FOOTER_TEXT = {
    "en": {
        "about": "Desire Agency in Lisbon. Fast, mobile-first websites for small businesses, in Portuguese, English and German. Payment after completion.",
        "site": "Site", "products": "Products", "follow": "Follow",
        "guide": "Agent Team Guide", "journal": "Free trading journal", "templates": "Free n8n templates",
        "newsletter": "Newsletter",
    },
    "de": {
        "about": "Desire Agency in Lissabon. Schnelle, mobilfreundliche Websites für kleine Betriebe, auf Portugiesisch, Englisch und Deutsch. Zahlung erst nach Fertigstellung.",
        "site": "Seite", "products": "Produkte", "follow": "Folgen",
        "guide": "Agent-Team-Guide (EN)", "journal": "Kostenloses Trading-Journal", "templates": "Kostenlose n8n-Vorlagen",
        "newsletter": "Newsletter",
    },
    "pt": {
        "about": "Desire Agency em Lisboa. Sites rápidos, pensados para o telemóvel, para pequenos negócios, em português, inglês e alemão. Pagamento só após conclusão.",
        "site": "Site", "products": "Produtos", "follow": "Seguir",
        "guide": "Agent Team Guide (EN)", "journal": "Trading journal gratuito (EN)", "templates": "Templates n8n gratuitos (EN)",
        "newsletter": "Newsletter",
    },
}


def split_h1(doc: str) -> str:
    """Pre-split h1 words into spans at build time (no DOM mutation -> no layout shift)."""
    import re as _re
    def fix(m):
        attrs, inner = m.group(1), m.group(2)
        parts = _re.split(r"(<[^>]+>[^<]*</[^>]+>)", inner)
        out, i = [], 0
        for part in parts:
            if part.startswith("<"):
                out.append(part.replace("<span ", f'<span style="--gd:{i * 45 + 120}ms" ', 1) if part.startswith("<span ") else part)
                i += 2
                continue
            for tok in _re.split(r"(\s+)", part):
                if not tok:
                    continue
                if tok.isspace():
                    out.append(tok)
                else:
                    out.append(f'<span class="w" style="--i:{i}">{tok}</span>')
                    i += 1
        if 'class="' in attrs:
            attrs = attrs.replace('class="', 'class="wsplit ', 1)
        else:
            attrs += ' class="wsplit"'
        return f"<h1{attrs}>{''.join(out)}</h1>"
    return _re.sub(r"<h1([^>]*)>(.*?)</h1>", fix, doc, count=1, flags=_re.S)


# Google Search Console ownership verification (meta tag on the home page + HTML file in the root).
GSC_TOKEN = "7efVrNpaPgdMJ_xsJqjmeh-chbtEHijNOpQQIeTPqA0"
GSC_FILE = "google20671475e05eab02.html"


def shell(lang: str, page: str, depth: int, title: str, description: str, body: str, extra_js: str = "", extra_head: str = "") -> str:
    paths = page_paths(lang, depth)
    root = paths["css"][: -len("css/site.css")]
    nav = []
    for key, label in NAV[lang]:
        if key == "legal":
            continue  # legal lives in the footer
        href = paths[key]
        cur = ' aria-current="page"' if key == page else ""
        if key == "websites":
            frm = T3(lang, "from €390", "ab 390 €", "desde 390 €")
            nav.append(f'<a class="nav-hot" href="{href}"{cur}>{esc(label)} <small>{frm}</small></a>')
            continue
        nav.append(f'<a href="{href}"{cur}>{esc(label)}</a>')
    other = T3(lang, "Deutsch", "English", "English")
    other_href = lang_href(lang, page, depth)
    en_cur = ' aria-current="true"' if lang == "en" else ""
    de_cur = ' aria-current="true"' if lang == "de" else ""
    wrap = "wrap-narrow" if page in ("n8n", "legal", "templates") else "wrap"
    dir_js = f'\n<script src="{paths["js_dir"]}" defer></script>' if page == "directory" else ""
    progress = '\n  <div class="progress" aria-hidden="true"></div>' if page in ("n8n", "templates", "legal") else ""
    canon = site_url(CANONICAL[(lang, page)])
    alt = ""
    if page == "websites":
        alt = (
            f'  <link rel="alternate" hreflang="en" href="{site_url(CANONICAL[("en", page)])}">\n'
            f'  <link rel="alternate" hreflang="de" href="{site_url(CANONICAL[("de", page)])}">\n'
            f'  <link rel="alternate" hreflang="pt-PT" href="{site_url(CANONICAL[("pt", page)])}">\n'
            f'  <link rel="alternate" hreflang="x-default" href="{site_url(CANONICAL[("en", page)])}">\n'
        )
    elif page != "templates":
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
    cur_attr = ' aria-current="true"'
    if page == "websites":
        sw = {"en": {"en": "#", "de": "../de/websites/", "pt": "../pt/websites/"},
              "de": {"en": "../../websites/", "de": "#", "pt": "../../pt/websites/"},
              "pt": {"en": "../../websites/", "de": "../../de/websites/", "pt": "#"}}[lang]
        lang_links = "".join(
            f'\n          <a href="{sw[c]}"{cur_attr if c == lang else ""} hreflang="{hl}" lang="{hl}">{c.upper()}</a>'
            for c, hl in (("en", "en"), ("de", "de"), ("pt", "pt-PT")))
    else:
        lang_links = (f'\n          <a href="{other_href if lang == "de" else "#"}"{en_cur} hreflang="en">EN</a>'
                      f'\n          <a href="{other_href if lang == "en" else "#"}"{de_cur} hreflang="de">DE</a>')
    gsc = ('\n  <meta name="google-site-verification" content="' + GSC_TOKEN + '" />') if (page == "home" and lang == "en") else ""
    return f"""<!DOCTYPE html>
<html lang="{"pt-PT" if lang == "pt" else lang}" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index, follow">{gsc}
  <meta name="description" content="{esc(description)}">
  <title>{esc(title)}</title>
  <link rel="canonical" href="{canon}">
{alt}  <meta name="theme-color" content="#06060c">
  <link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
  <link rel="manifest" href="{root}site.webmanifest">
{png_icons}  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Desire Agency">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{canon}">
{og_tags}  <meta property="og:locale" content="{T3(lang, "en_US", "de_DE", "pt_PT")}">
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
  <a class="skip" href="#content">{T3(lang, "Skip to content", "Zum Inhalt", "Saltar para o conteúdo")}</a>
  <header class="site-header">
    <div class="header-inner wrap">
      <a class="brand" href="{paths['home']}">
        {LOGO_SVG}
        <span class="brand-text">
          <span class="brand-name">Desire<span class="wm-2"> Agency</span></span>
          <span class="brand-tag">{T3(lang, "An AI agent team, built in public", "KI-Agenten-Team, öffentlich gebaut", "Equipa de agentes de IA, construída em público")}</span>
        </span>
      </a>
      <nav aria-label="{T3(lang, "Main", "Hauptnavigation", "Navegação principal")}">
        {''.join(nav)}
        <a class="btn btn-primary btn-sm nav-cta" href="{esc(SUBSCRIBE_URL)}">{esc(sub_label)}</a>
        <span class="lang{" lang-3" if page == "websites" else ""}" aria-label="Language">{lang_links}
        </span>
      </nav>
      <button type="button" class="theme-toggle" aria-label="{T3(lang, "Toggle theme", "Design wechseln", "Mudar tema")}">{THEME_ICONS}</button>
    </div>
  </header>{progress}
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
            <li><a href="{paths['legal']}">{T3(lang, "Legal notice / Impressum", "Impressum / Kontakt", "Aviso legal / Impressum (EN)")}</a></li>
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
        <p>© 2026 Desire Agency · Lisboa · {T3(lang, "No cookies, no tracking.", "Keine Cookies, kein Tracking.", "Sem cookies, sem rastreio.")}</p>
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
        "title": "Desire Agency — websites for small businesses, from Lisbon",
        "description": "Fast, mobile-first websites for small businesses, built in Lisbon. Packages Vitrine, Atelier and Maison in Portuguese, English or German. Payment after completion. Free n8n templates and a sourced tool directory.",
        "eyebrow": "From Lisbon · PT, EN, DE",
        "h1_a": "One person. A team of AI agents.",
        "h1_b": "Websites for small businesses.",
        "lede": "We design fast, mobile-first websites for cafés, shops and local businesses, and run them with a small AI agent team. You get a written quote first and pay only after completion.",
        "cta_news": "Get the build log",
        "cta_web": "Get a website — from €390",
        "cta_guide": "Guide: $9 early bird",
        "guide_note": "Early bird $9 instead of $19 for the first 50 (code EARLYBIRD).",
        "web_line": "We build fast, mobile-first websites for small businesses. Final prices, written quote first.",
        "link_tpl": "Free n8n templates",
        "link_journal": "Free trading journal",
        "link_n8n": "Why we recommend n8n",
        "hero_note": "Portuguese, English and German. Based in Lisbon.",
        "offer_title": "What you get",
        "offer_meta": "Lisbon · PT, EN, DE",
        "offer": [
            ("Vitrine", "from 390 €"),
            ("Atelier", "from 750 €"),
            ("Maison", "from 1,190 €"),
        ],
        "offer_foot": "Payment after completion. Written quote first.",
        "offer_link": "See packages",
        "bip_kicker": "The studio",
        "bip_title": "What we work with",
        "bip_text": "A small AI agent team in Lisbon, demo sites you can click through, and free starting points for your own automation.",
        "stats": [
            ("11", "AI agents", "10 specialist bots and one chief of staff, coordinated by one person."),
            ("6", "Demo sites", "Fictional example businesses, clearly labelled as demos."),
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
        "rules_title": "How we work with you",
        "rules": [
            "Written quote first, payment only after completion.",
            "Sites in Portuguese, English or German, from Lisbon.",
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
                "text": "A field report: how one person works with ten AI agents, what each one does, and how the day-to-day workflow is set up.",
                "price": "$19", "price_sub": "$9 early bird for the first 50, code <code>EARLYBIRD</code>",
                "cta": "Get the guide", "url": GUIDE_EARLY_URL,
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
        "rev": "A sourced look at the automation tools we use, with prices taken from official pages.",
        "news_title": "The build log",
        "news_text": "A short, free newsletter from Desire Agency about the websites, templates and tools we are building in Lisbon.",
        "news_cta": "Get the build log",
        "follow_text": "Or follow along:",
    },
    "de": {
        "title": "Desire Agency — Websites für kleine Betriebe, aus Lissabon",
        "description": "Schnelle, mobilfreundliche Websites für kleine Betriebe, gebaut in Lissabon. Pakete Vitrine, Atelier und Maison auf Portugiesisch, Englisch oder Deutsch. Zahlung erst nach Fertigstellung. Kostenlose n8n-Vorlagen und ein Tool-Verzeichnis mit Quellen.",
        "eyebrow": "Aus Lissabon · PT, EN, DE",
        "h1_a": "Eine Person. Ein Team aus KI-Agenten.",
        "h1_b": "Websites für kleine Betriebe.",
        "lede": "Wir gestalten schnelle, mobilfreundliche Websites für Cafés, Läden und lokale Betriebe und betreiben sie mit einem kleinen KI-Agenten-Team. Du bekommst zuerst ein schriftliches Angebot und zahlst erst nach Fertigstellung.",
        "cta_news": "Build-Log abonnieren",
        "cta_web": "Website anfragen — ab 390 €",
        "cta_guide": "Guide: 9 $ Early Bird",
        "guide_note": "Early Bird 9 $ statt 19 $ für die ersten 50 (Code EARLYBIRD). Guide auf Englisch.",
        "web_line": "Wir bauen schnelle, mobilfreundliche Websites für kleine Betriebe. Endpreise, erst ein schriftliches Angebot.",
        "link_tpl": "Kostenlose n8n-Vorlagen",
        "link_journal": "Kostenloses Trading-Journal",
        "link_n8n": "Warum wir n8n empfehlen",
        "hero_note": "Portugiesisch, Englisch und Deutsch. Sitz in Lissabon.",
        "offer_title": "Was du bekommst",
        "offer_meta": "Lissabon · PT, EN, DE",
        "offer": [
            ("Vitrine", "ab 390 €"),
            ("Atelier", "ab 750 €"),
            ("Maison", "ab 1.190 €"),
        ],
        "offer_foot": "Zahlung erst nach Fertigstellung. Zuerst ein schriftliches Angebot.",
        "offer_link": "Pakete ansehen",
        "bip_kicker": "Das Studio",
        "bip_title": "Womit wir arbeiten",
        "bip_text": "Ein kleines KI-Agenten-Team in Lissabon, Demo-Seiten zum Durchklicken und kostenlose Einstiege für deine eigene Automatisierung.",
        "stats": [
            ("11", "KI-Agenten", "10 spezialisierte Bots und ein Chief of Staff, koordiniert von einer Person."),
            ("6", "Demo-Seiten", "Fiktive Beispielbetriebe, klar als Demos gekennzeichnet."),
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
        "rules_title": "So arbeiten wir mit dir",
        "rules": [
            "Zuerst ein schriftliches Angebot, Zahlung erst nach Fertigstellung.",
            "Websites auf Portugiesisch, Englisch oder Deutsch, aus Lissabon.",
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
                "text": "Ein Praxisbericht: wie eine Person mit zehn KI-Agenten arbeitet, was jeder davon macht und wie der Arbeitsalltag aufgebaut ist. Auf Englisch.",
                "price": "19 $", "price_sub": "9 $ Early Bird für die ersten 50, Code <code>EARLYBIRD</code>",
                "cta": "Zum Guide", "url": GUIDE_EARLY_URL,
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
        "rev": "Ein quellenbelegter Blick auf die Automatisierungs-Tools, die wir nutzen, mit Preisen von offiziellen Seiten.",
        "news_title": "Das Build-Log",
        "news_text": "Ein kurzer, kostenloser Newsletter von Desire Agency über die Websites, Vorlagen und Tools, die wir in Lissabon bauen.",
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
        "trade": "Research & markets", "growth": "Growth & products", "lead_grp": "Coordination", "human_grp": "Owner",
        "hint": "Lines show who reports to the chief of staff.",
        "human": ("Desire", "Human owner", "Sets the goals and approves anything involving real money, purchases or deals."),
        "lead": ("Jojo", "Chief of staff", "Plans the day, hands out work, checks results and writes the morning and evening reports."),
        "trade_agents": [
            ("Chef", "Desk manager", "Runs the internal market-research desks and proposes rule changes."),
            ("Scout", "Candidate scout", "Looks for new candidates for the research desks."),
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
        "trade": "Recherche & Märkte", "growth": "Wachstum & Produkte", "lead_grp": "Koordination", "human_grp": "Owner",
        "hint": "Die Linien zeigen, wer an den Chief of Staff berichtet.",
        "human": ("Desire", "Owner (Mensch)", "Setzt die Ziele und gibt alles frei, was echtes Geld, Käufe oder Deals betrifft."),
        "lead": ("Jojo", "Chief of Staff", "Plant den Tag, verteilt Aufgaben, prüft Ergebnisse und schreibt den Morgen- und Abendbericht."),
        "trade_agents": [
            ("Chef", "Desk-Manager", "Führt die internen Markt-Recherche-Desks und schlägt Regeländerungen vor."),
            ("Scout", "Kandidaten-Scout", "Sucht neue Kandidaten für die Recherche-Desks."),
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
        "kicker": "FAQ", "title": "Questions",
        "items": [
            ("How does payment work?", "You get a written quote by email first. You pay only after completion, with no deposit."),
            ("Which languages do you work in?", "Portuguese, English and German. The studio is based in Lisbon."),
            ("Can I see examples?", "Yes. The demo sites are fictional example businesses and are clearly labelled as demos. This website itself is a live example of the same approach."),
            ("Are the n8n templates really free?", "Yes. You download the workflow.json, import it into your own n8n and add your own credentials. The files only contain placeholders."),
            ("Does this site track me?", "No. There are no cookies, analytics or third-party requests. The theme toggle saves your choice in your own browser only."),
        ],
    },
    "de": {
        "kicker": "FAQ", "title": "Häufige Fragen",
        "items": [
            ("Wie funktioniert die Zahlung?", "Du bekommst zuerst ein schriftliches Angebot per E-Mail. Du zahlst erst nach Fertigstellung, ohne Anzahlung."),
            ("In welchen Sprachen arbeitet ihr?", "Auf Portugiesisch, Englisch und Deutsch. Das Studio sitzt in Lissabon."),
            ("Kann ich Beispiele sehen?", "Ja. Die Demo-Seiten sind fiktive Beispielbetriebe und klar als Demos gekennzeichnet. Diese Website selbst ist ein live laufendes Beispiel für denselben Ansatz."),
            ("Sind die n8n-Vorlagen wirklich kostenlos?", "Ja. Du lädst die workflow.json herunter, importierst sie in dein eigenes n8n und trägst deine eigenen Zugangsdaten ein. Die Dateien enthalten nur Platzhalter."),
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
    "en": {"kicker": "How we work", "title": "From brief to launch",
           "text": "Clear steps, a written quote first, and payment only after completion.",
           "steps": [
               ("01", "Brief", "You send texts, photos and your logo. We reply with a written quote by email."),
               ("02", "Build", "We design a fast, mobile-first site in Portuguese, English or German."),
               ("03", "Review", "You go through the revision rounds included in the package."),
               ("04", "Launch", "The site goes live. You pay only after completion, with no deposit."),
           ]},
    "de": {"kicker": "So arbeiten wir", "title": "Vom Briefing zur fertigen Seite",
           "text": "Klare Schritte, zuerst ein schriftliches Angebot, Zahlung erst nach Fertigstellung.",
           "steps": [
               ("01", "Briefing", "Du schickst Texte, Fotos und dein Logo. Du bekommst ein schriftliches Angebot per E-Mail."),
               ("02", "Umsetzung", "Wir gestalten eine schnelle, mobilfreundliche Seite auf Portugiesisch, Englisch oder Deutsch."),
               ("03", "Korrektur", "Du gehst die Korrekturrunden durch, die im Paket enthalten sind."),
               ("04", "Launch", "Die Seite geht live. Du zahlst erst nach Fertigstellung, ohne Anzahlung."),
           ]},
}

STACK = {
    "en": {"kicker": "Built with", "title": "A small, lean stack", "text": "Static files, no trackers, no build server. These are the tools the system actually runs on."},
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
           "text": "Our own site is the first project. New design system, motion, a team diagram and EN/DE, still static and tracker-free.",
           "before": "Before · 20 Nov 2026", "after": "After · 21 Nov 2026",
           "points": ["Self-hosted font, no third-party requests", "Light and dark theme, reduced-motion support", "Canonical, hreflang, Open Graph, sitemap and llms.txt", "Hosted on GitHub Pages, no hosting fee for the public site"],
           "alt_before": "Screenshot of the old Desire Agency home page: serif headings on a beige background", "alt_after": "Screenshot of the new Desire Agency home page: dark redesigned hero", "cta": "Want a site like this?"},
    "de": {"kicker": "Fallstudie", "title": "Diese Website, an einem Abend neu gebaut",
           "text": "Unsere eigene Seite ist das erste Projekt. Neues Design-System, Animationen, ein Team-Schaubild und EN/DE, weiterhin statisch und ohne Tracker.",
           "before": "Vorher · 20.11.2026", "after": "Nachher · 21.11.2026",
           "points": ["Schrift selbst gehostet, keine Anfragen an Dritte", "Helles und dunkles Design, Rücksicht auf reduzierte Bewegung", "Canonical, hreflang, Open Graph, Sitemap und llms.txt", "Gehostet auf GitHub Pages, ohne Hosting-Gebühr für die öffentliche Seite"],
           "alt_before": "Screenshot der alten Desire-Agency-Startseite: Serifen-Überschriften auf beigem Hintergrund", "alt_after": "Screenshot der neuen Desire-Agency-Startseite: dunkler, neu gestalteter Hero", "cta": "Auch so eine Website?"},
    "pt": {"kicker": "Caso real", "title": "Este site, refeito numa noite",
           "text": "O nosso próprio site é o primeiro projeto. Novo sistema de design, animações e EN/DE, continua estático e sem rastreio.",
           "before": "Antes · 20.11.2026", "after": "Depois · 21.11.2026",
           "points": ["Tipo de letra alojado no próprio site, sem pedidos a terceiros", "Tema claro e escuro, respeita a preferência por menos movimento", "Canonical, hreflang, Open Graph, sitemap e llms.txt", "Alojado no GitHub Pages, sem taxa de alojamento para o site público"],
           "alt_before": "Captura de ecrã da antiga página inicial da Desire Agency: títulos com serifa sobre fundo bege", "alt_after": "Captura de ecrã da nova página inicial da Desire Agency: topo escuro redesenhado", "cta": "Quer um site assim?"},
}
COMPARE = {
    "en": {"label": "Before and after comparison. Move the slider to show more of the old or the new site.", "hint": "Drag to compare", "vt": "{n}% old site visible"},
    "de": {"label": "Vorher-Nachher-Vergleich. Schieberegler bewegen, um mehr von der alten oder der neuen Seite zu sehen.", "hint": "Zum Vergleichen ziehen", "vt": "{n}% alte Seite sichtbar"},
    "pt": {"label": "Comparação antes e depois. Mova o controlo para ver mais do site antigo ou do novo.", "hint": "Arraste para comparar", "vt": "{n}% do site antigo visível"},
}
WEB_ROT = {
    "en": ("Built for", ["cafés", "barbershops", "restaurants", "shoe repair shops", "tradespeople"]),
    "de": ("Gemacht für", ["Cafés", "Barbershops", "Restaurants", "Schuhmacher", "Handwerker"]),
    "pt": ("Feito para", ["cafés", "barbearias", "restaurantes", "sapateiros", "faz-tudo"]),
}


def compare_widget(lang: str, root: str) -> str:
    """Before/after slider: native range input (implicit role=slider) over two stacked screenshots.
    Without JS it shows a static 50/50 split; site.js syncs --pos and aria-valuetext."""
    t, c = CASE[lang], COMPARE[lang]
    img = lambda src, alt: f'<img src="{root}img/{src}" width="960" height="600" loading="lazy" decoding="async" alt="{esc(alt)}">'
    return (f'<figure class="mock compare" style="--pos:50%"><div class="mock-bar" aria-hidden="true"><i></i><i></i><i></i><span>maximussoroka.github.io</span></div>'
            f'<div class="compare-stage">{img("case-after.svg", t["alt_after"])}<div class="compare-before">{img("case-before.svg", t["alt_before"])}</div>'
            f'<span class="compare-tag is-b" aria-hidden="true">{esc(t["before"])}</span><span class="compare-tag is-a" aria-hidden="true">{esc(t["after"])}</span>'
            f'<span class="compare-handle" aria-hidden="true"><span></span></span>'
            f'<input class="compare-range" type="range" min="0" max="100" value="50" step="1" aria-label="{esc(c["label"])}" aria-valuetext="{esc(c["vt"].format(n=50))}" data-vt="{esc(c["vt"])}"></div>'
            f'<figcaption><span>{esc(t["before"])}</span><span class="compare-hint" aria-hidden="true">← {esc(c["hint"])} →</span><span class="is-after-cap">{esc(t["after"])}</span></figcaption></figure>')


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


def case_section(lang: str, paths: dict, cta_href: str = "") -> str:
    t = CASE[lang]
    root = paths["css"][: -len("css/site.css")]
    cta_href = cta_href or paths["websites"]
    pts = "".join(f"<li>{esc(x)}</li>" for x in t["points"])
    def frame(src, cap, alt, cls=""):
        return (f'<figure class="mock {cls}"><div class="mock-bar" aria-hidden="true"><i></i><i></i><i></i><span>maximussoroka.github.io</span></div>'
                f'<img src="{root}img/{src}" width="960" height="600" loading="lazy" decoding="async" alt="{esc(alt)}"><figcaption>{esc(cap)}</figcaption></figure>')
    return f"""
      <section class="section" id="case-study">
        <div class="section-head"><div><p class="kicker">{esc(t["kicker"])}</p><h2>{esc(t["title"])}</h2><p>{esc(t["text"])}</p></div></div>
        <div class="case">
          <div class="case-shots is-compare">
            {compare_widget(lang, root)}
          </div>
          <div><ul class="checks">{pts}</ul>
          <p style="margin:1.2rem 0 0"><a class="btn btn-ghost" href="{cta_href}">{esc(t["cta"])} <span class="arrow" aria-hidden="true">→</span></a></p></div>
        </div>
      </section>
"""


CONTACT_EMAIL = "desire.studio.agency@gmail.com"

WEBSITES = {
    "en": {
        "title": "Websites for small businesses — Desire Agency",
        "description": "Fast, mobile-first websites for small businesses, built by Desire Agency in Lisbon. Vitrine from €390, Atelier from €750, Maison from €1,190, Care €29/month. Final prices, no VAT charged. No builder subscription, no tracking unless you want it.",
        "kicker": "Websites", "h1": "Fast, honest websites for small businesses",
        "lede": "A clean site that works on the phone, brings enquiries and belongs to you. No builder subscription and no tracking unless you want it. Built by the same team that runs this site.",
        "status": "Send the form or an email and you get a written quote by email first. Payment after completion – no deposit.",
        "vat": "Final prices. No VAT charged – exempt under Art. 53 CIVA (Portugal).",
        "from": "from", "per_month": "/ month",
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
        "description": "Schnelle, mobilfreundliche Websites für kleine Betriebe, gebaut von Desire Agency in Lissabon. Vitrine ab 390 €, Atelier ab 750 €, Maison ab 1.190 €, Care 29 €/Monat. Endpreise, keine MwSt. Kein Baukasten-Abo, kein Tracking, wenn du keines willst.",
        "kicker": "Websites", "h1": "Schnelle, ehrliche Websites für kleine Betriebe",
        "lede": "Eine klare Seite, die auf dem Handy funktioniert, Anfragen bringt und dir gehört. Kein Baukasten-Abo und kein Tracking, wenn du keines willst. Gebaut vom selben Team, das diese Seite betreibt.",
        "status": "Formular oder E-Mail genügt: Du bekommst zuerst ein schriftliches Angebot per E-Mail. Zahlung erst nach Fertigstellung – keine Anzahlung.",
        "vat": "Endpreise. Keine MwSt. – Steuerbefreiung nach Art. 53 CIVA (Portugal).",
        "from": "ab", "per_month": "/ Monat",
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
    "pt": {
        "title": "Sites para pequenos negócios em Lisboa — Desire Agency",
        "description": "Sites rápidos, pensados para o telemóvel, para pequenos negócios em Lisboa. Vitrine a partir de 390 €, Atelier a partir de 750 €, Maison a partir de 1190 €, Care 29 €/mês. Preços finais, IVA isento. Sem mensalidade de construtor de sites.",
        "kicker": "Sites", "h1": "Sites rápidos e honestos para pequenos negócios",
        "lede": "Um site limpo, que funciona bem no telemóvel, traz contactos de clientes e é seu. Sem mensalidade de construtor de sites e sem rastreio, a não ser que o queira. Feito pela mesma equipa que gere este site, a partir de Lisboa.",
        "status": "Basta o formulário ou um e-mail: recebe primeiro um orçamento por escrito, por e-mail. Pagamento só após conclusão – sem sinal.",
        "vat": "Preços finais. IVA isento ao abrigo do artigo 53.º do CIVA.",
        "from": "a partir de", "per_month": "/ mês",
        "delivery": "Prazo", "revisions": "Revisões",
        "ask": "Pedir o {name}", "subject": "Pedido {name}",
        "common_title": "Incluído em todos os pacotes",
        "common": ["Design cuidado, pensado primeiro para o telemóvel, no estilo deste site", "Uma ação principal clara: WhatsApp, chamada ou formulário", "SEO técnico: títulos, descrições, sitemap, robots.txt, imagem de pré-visualização", "Páginas legais básicas; sem rastreio, a não ser que o peça", "Alojamento no GitHub Pages com HTTPS no primeiro ano; os ficheiros são seus", "Domínio registado em seu nome (a taxa do registo é paga por si ou cobrada ao preço de custo)"],
        "packages": [
            ("Vitrine", "Site de uma página", "Para um negócio local ou uma única oferta.", ["Uma página longa, num idioma (PT, EN ou DE)", "Botão de WhatsApp e/ou formulário de contacto", "SEO básico e imagem de pré-visualização"], "390 €", False, "5–7 dias úteis", "2 rondas"),
            ("Atelier", "Site de empresa, 3–5 páginas", "Para negócios que precisam de mais do que uma página.", ["Tudo o que o Vitrine inclui", "Até 5 páginas, num idioma", "Navegação, página 404 e rodapé comum", "Mapa incorporado e ligações aos seus perfis (opcional)"], "750 €", False, "10–14 dias úteis", "2 rondas"),
            ("Maison", "Até 8 páginas, dois idiomas", "Para público internacional ou turístico.", ["Tudo o que o Atelier inclui", "Até 8 páginas, dois idiomas com seletor", "SEO por idioma com hreflang"], "1190 €", False, "14–21 dias úteis", "3 rondas"),
            ("Care", "Manutenção mensal (opcional)", "Mantém o site a funcionar depois do lançamento. Pode cancelar com 30 dias de aviso prévio.", ["Alojamento e HTTPS", "Monitorização e aviso se o site for abaixo", "Cópias de segurança através do histórico Git", "Pequenas alterações de conteúdo, até 30 minutos por mês"], "29 €", True, "", ""),
        ],
        "time_note": "Os prazos contam a partir do briefing completo (textos, fotografias, logótipo, acessos), não da primeira mensagem.",
        "not": "Não inclui: lojas online, sistemas de reservas, áreas de cliente, WordPress, design de logótipo, fotografia, campanhas de publicidade. Tudo o que vá além do pacote é orçamentado antes de começarmos.",
        "example": "Exemplo real: este site.",
        "contact": "Tem dúvidas? Escreva-nos",
    },
}


def _mailto(subject: str) -> str:
    from urllib.parse import quote
    return f"mailto:{CONTACT_EMAIL}?subject={quote(subject)}"


DEMOS = [
    ("barbearia", {"en": "Barbershop · Lisbon (PT)", "de": "Barbershop · Lissabon (PT)", "pt": "Barbearia · Lisboa (PT)"}, "Barbearia Navalha d'Ouro",
     {"en": "Dark, classic look: prices, gallery, reviews, opening hours, sticky booking button.", "de": "Dunkler, klassischer Look: Preise, Galerie, Bewertungen, Öffnungszeiten, fixierter Buchungsbutton.", "pt": "Visual clássico e escuro: preços, galeria, avaliações, horário, botão de marcação fixo."}),
    ("tasca", {"en": "Restaurant / tasca · Lisbon (PT + EN)", "de": "Restaurant / Tasca · Lissabon (PT + EN)", "pt": "Restaurante / tasca · Lisboa (PT + EN)"}, "Tasca do Pátio Azul",
     {"en": "Bilingual (Maison): dish of the day, menu, gallery, reviews, hours, call to book.", "de": "Zweisprachig (Maison): Tagesgericht, Speisekarte, Galerie, Bewertungen, Öffnungszeiten.", "pt": "Bilingue (Maison): prato do dia, ementa, galeria, avaliações, horário, ligar para reservar."}),
    ("natal", {"en": "Christmas campaign · Lisbon tasca (PT + EN)", "de": "Weihnachtskampagne · Tasca Lissabon (PT + EN)", "pt": "Campanha de Natal · tasca em Lisboa (PT + EN)"}, "Tasca do Lume Calmo",
     {"en": "One-page holiday campaign (Vitrine): Christmas Eve menu, gift vouchers, festive hours and a booking button.", "de": "Einseitige Weihnachtskampagne (Vitrine): Festmenü, Geschenkgutscheine, Feiertagszeiten und Reservierungsbutton.", "pt": "Campanha de Natal numa página (Vitrine): menu da Consoada, vales de oferta, horário de festas e botão de reserva."}),
    ("sapateiro", {"en": "Shoe repair & keys · Lisbon (PT)", "de": "Schuhmacher & Schlüssel · Lissabon (PT)", "pt": "Sapateiro & chaves · Lisboa (PT)"}, "Sapataria Meia-Sola",
     {"en": "Repair price list, quote by photo in 3 steps, reviews, opening hours.", "de": "Preisliste für Reparaturen, Angebot per Foto in 3 Schritten, Bewertungen, Öffnungszeiten.", "pt": "Tabela de arranjos, orçamento por foto em 3 passos, avaliações, horário."}),
    ("cafe", {"en": "Café · Dublin (EN)", "de": "Café · Dublin (EN)", "pt": "Café · Dublin (EN)"}, "Linden & Oat",
     {"en": "Menu board, daily bake the owner edits, gallery, reviews, opening hours.", "de": "Menütafel, Tagesgebäck zum Selbst-Ändern, Galerie, Bewertungen, Öffnungszeiten.", "pt": "Quadro de ementa, bolo do dia editável pelo dono, galeria, avaliações, horário."}),
    ("handyman", {"en": "Handyman / trades · Bristol (EN)", "de": "Handwerker · Bristol (EN)", "pt": "Faz-tudo / ofícios · Bristol (EN)"}, "Tidy Joist",
     {"en": "Services with starting prices, quote by photo, service area, reviews, sticky call button.", "de": "Leistungen mit Ab-Preisen, Angebot per Foto, Einsatzgebiet, Bewertungen, fixierter Anruf-Button.", "pt": "Serviços com preços base, orçamento por foto, zona de serviço, avaliações, botão de chamada fixo."}),
]

WEB_EXTRA = {
    "en": {
        "demos_h": "Demos", "demos_p": "Six example sites for typical small businesses in Lisbon, Dublin and Bristol, each with its own look, including a Christmas campaign page. The businesses are fictional; the pages show what your site can look like on your phone.",
        "demo_label": "Demo – fictional business", "demo_open": "Open demo",
        "form_h": "Send an enquiry", "form_p": "Tell us a little about your business. We reply by email with questions or a written quote. No obligation.",
        "f_name": "Name", "f_email": "Email", "f_biz": "Business name or current website (optional)", "f_pkg": "Package",
        "f_pkg_opts": ["Not sure yet", "Vitrine", "Atelier", "Maison", "Care"], "f_msg": "Message", "f_send": "Send enquiry",
        "privacy": "Privacy: we use your details only to answer your enquiry. The form is delivered to our inbox by FormSubmit (formsubmit.co); this site stores nothing. No newsletter, no sharing.",
        "fallback": "Prefer email? Write to", "thanks": "Thank you – your message was sent. We will reply by email.",
        "subject": "New enquiry (EN) – Websites",
    },
    "de": {
        "demos_h": "Demos", "demos_p": "Sechs Beispielseiten für typische kleine Betriebe in Lissabon, Dublin und Bristol, jede mit eigenem Look, darunter eine Weihnachtskampagne. Die Betriebe sind erfunden; die Seiten zeigen, wie deine Seite auf dem Handy aussehen kann.",
        "demo_label": "Demo – fiktiver Betrieb", "demo_open": "Demo öffnen",
        "form_h": "Anfrage senden", "form_p": "Erzähl uns kurz von deinem Betrieb. Wir antworten per E-Mail mit Rückfragen oder einem schriftlichen Angebot. Unverbindlich.",
        "f_name": "Name", "f_email": "E-Mail", "f_biz": "Name des Betriebs oder aktuelle Website (optional)", "f_pkg": "Paket",
        "f_pkg_opts": ["Noch unsicher", "Vitrine", "Atelier", "Maison", "Care"], "f_msg": "Nachricht", "f_send": "Anfrage senden",
        "privacy": "Datenschutz: Wir nutzen deine Angaben nur, um deine Anfrage zu beantworten. Das Formular wird über FormSubmit (formsubmit.co) an unser Postfach zugestellt; diese Seite speichert nichts. Kein Newsletter, keine Weitergabe.",
        "fallback": "Lieber per E-Mail? Schreib an", "thanks": "Danke – deine Nachricht wurde gesendet. Wir antworten per E-Mail.",
        "subject": "Neue Anfrage (DE) – Websites",
    },
    "pt": {
        "demos_h": "Demos", "demos_p": "Seis exemplos para pequenos negócios típicos em Lisboa, Dublin e Bristol, cada um com o seu estilo, incluindo uma campanha de Natal. Os negócios são fictícios; as páginas mostram como o seu site pode ficar no telemóvel.",
        "demo_label": "Exemplo / demo – negócio fictício", "demo_open": "Ver demo",
        "form_h": "Pedir orçamento", "form_p": "Conte-nos um pouco sobre o seu negócio. Respondemos por e-mail com perguntas ou um orçamento por escrito. Sem compromisso.",
        "f_name": "Nome", "f_email": "E-mail", "f_biz": "Nome do negócio ou site atual (opcional)", "f_pkg": "Pacote",
        "f_pkg_opts": ["Ainda não sei", "Vitrine", "Atelier", "Maison", "Care"], "f_msg": "Mensagem", "f_send": "Enviar pedido",
        "privacy": "Privacidade: usamos os seus dados apenas para responder ao seu pedido. O formulário é entregue na nossa caixa de correio através do FormSubmit (formsubmit.co); este site não guarda nada. Sem newsletter, sem partilha com terceiros.",
        "fallback": "Prefere e-mail? Escreva para", "thanks": "Obrigado – a sua mensagem foi enviada. Respondemos por e-mail.",
        "subject": "Novo pedido (PT) – Sites",
    },
}

FORM_ACTION = "https://formsubmit.co/" + "desire.studio.agency@gmail.com"


def demos_href(lang: str) -> str:
    return "../demos/" if lang == "en" else "../../demos/"


def portfolio_section(lang: str) -> str:
    x = WEB_EXTRA[lang]
    base = demos_href(lang)
    cards = "".join(f"""
          <a class="product demo-card" href="{base}{slug}/">
            <span class="pill">{esc(x["demo_label"])}</span>
            <h3>{esc(name)}</h3>
            <p><strong>{esc(niche[lang])}</strong> · {esc(desc[lang])}</p>
            <span class="text-link">{esc(x["demo_open"])} →</span>
          </a>""" for slug, niche, name, desc in DEMOS)
    return f"""
      <section class="section" id="demos">
        <div class="section-head"><h2>{esc(x["demos_h"])}</h2><p>{esc(x["demos_p"])}</p></div>
        <div class="products demo-grid">{cards}
        </div>
      </section>"""


def contact_form(lang: str) -> str:
    x = WEB_EXTRA[lang]
    nxt = site_url(CANONICAL[(lang, "websites")]) + "?enviado=1#obrigado"
    opts = "".join(f'<option value="{esc(o)}">{esc(o)}</option>' for o in x["f_pkg_opts"])
    return f"""
      <section class="section" id="contacto">
        <div class="section-head"><h2>{esc(x["form_h"])}</h2><p>{esc(x["form_p"])}</p></div>
        <p class="notice notice-info form-thanks" id="obrigado" role="status">{esc(x["thanks"])}</p>
        <form class="panel contact-form" action="{FORM_ACTION}" method="POST" accept-charset="UTF-8">
          <input type="hidden" name="_subject" value="{esc(x["subject"])}">
          <input type="hidden" name="_captcha" value="true">
          <input type="hidden" name="_template" value="table">
          <input type="hidden" name="_next" value="{esc(nxt)}">
          <input type="hidden" name="origem" value="{lang}" id="origem">
          <div class="hp" aria-hidden="true"><label>Leave empty <input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div>
          <div class="form-row">
            <label>{esc(x["f_name"])}<input type="text" name="name" required autocomplete="name" maxlength="120"></label>
            <label>{esc(x["f_email"])}<input type="email" name="email" required autocomplete="email" maxlength="160"></label>
          </div>
          <label>{esc(x["f_biz"])}<input type="text" name="negocio" maxlength="200"></label>
          <label>{esc(x["f_pkg"])}<select name="pacote">{opts}</select></label>
          <label>{esc(x["f_msg"])}<textarea name="message" rows="5" required maxlength="3000"></textarea></label>
          <p class="note form-privacy">{esc(x["privacy"])}</p>
          <div class="actions"><button class="btn btn-primary" type="submit">{esc(x["f_send"])} <span class="arrow" aria-hidden="true">→</span></button></div>
          <p class="note">{esc(x["fallback"])} <a href="{esc(_mailto(WEBSITES[lang]["subject"].format(name="Website")))}">{CONTACT_EMAIL}</a>.</p>
        </form>
        <script>(function(){{try{{var q=new URLSearchParams(location.search),o=document.getElementById("origem"),u=["utm_source","utm_medium","utm_campaign","utm_content"].map(function(k){{return q.get(k)?k+"="+q.get(k):""}}).filter(Boolean).join("&");if(o&&u)o.value=o.value+" | "+u.slice(0,200)}}catch(e){{}}}})();</script>
      </section>"""


def websites_body(lang: str) -> str:
    t = WEBSITES[lang]
    paths = page_paths(lang, 1 if lang == "en" else 2)
    if lang == "pt":
        paths = dict(paths, home="../../")
    cards = []
    for i, (name, sub, who, feats, price, monthly, delivery, revs) in enumerate(t["packages"]):
        fl = "".join(f"<li>{esc(f)}</li>" for f in feats)
        meta = ""
        if delivery:
            meta = (f'<dl class="pkg-meta"><div><dt>{esc(t["delivery"])}</dt><dd>{esc(delivery)}</dd></div>'
                    f'<div><dt>{esc(t["revisions"])}</dt><dd>{esc(revs)}</dd></div></dl>')
        pre = "" if monthly else f'<span class="price-from">{esc(t["from"])}</span>'
        post = f'<span class="price-sub">{esc(t["per_month"])}</span>' if monthly else ""
        btn = "btn btn-primary" if i == 1 else "btn btn-ghost"
        cards.append(f"""
          <article class="product pkg{" is-featured" if i == 1 else ""}" id="pkg-{name.lower()}">
            <span class="pill">{esc(sub)}</span>
            <h3>{esc(name)}</h3>
            <p>{esc(who)}</p>
            <div class="price-line">{pre}<span class="price-big">{esc(price)}</span>{post}</div>
            <ul class="checks checks-sm">{fl}</ul>
            {meta}
            <div class="actions"><a class="{btn}" href="{esc(_mailto(t["subject"].format(name=name)))}">{esc(t["ask"].format(name=name))} <span class="arrow" aria-hidden="true">→</span></a></div>
          </article>""")
    common = "".join(f"<li>{esc(c)}</li>" for c in t["common"])
    rl, rw = WEB_ROT[lang]
    rot = "".join(f'<span class="rot-w{" is-on" if i == 0 else ""}">{esc(w)}</span>' for i, w in enumerate(rw))
    return f"""
      <header class="hero web-hero">
        <div class="aurora" aria-hidden="true"><i></i><i></i><i></i></div>
        <p class="kicker">{esc(t["kicker"])}</p>
        <h1 class="page-title">{esc(t["h1"])}</h1>
        <p class="rotator">{esc(rl)} <span class="rot" aria-hidden="true">{rot}</span><span class="visually-hidden">{esc(", ".join(rw))}</span></p>
        <p class="lede">{esc(t["lede"])}</p>
        <p class="notice notice-info" role="note">{esc(t["status"])}</p>
      </header>
      <h2 class="visually-hidden">{T3(lang, "Packages", "Pakete", "Pacotes")}</h2>
      <div class="products products-4">{''.join(cards)}
      </div>
      <p class="note">{esc(t["vat"])} {esc(t["time_note"])}</p>
      <section class="section">
        <div class="split">
          <div class="panel"><h3>{esc(t["common_title"])}</h3><ul class="checks">{common}</ul></div>
          <div class="panel"><p>{esc(t["not"])}</p><p><a href="#case-study">{esc(t["example"])}</a></p>
            <p><a class="btn btn-ghost" href="#contacto">{esc(t["contact"])} <span class="arrow" aria-hidden="true">→</span></a></p></div>
        </div>
      </section>{portfolio_section(lang)}{case_section(lang, paths, "#contacto")}{contact_form(lang)}
"""


def home_body(lang: str, paths: dict) -> str:
    t = HOME[lang]
    offer = "\n".join(
        f'<div class="ledger-row"><span>{esc(label)}</span><b>{esc(val)}</b></div>'
        for label, val in t["offer"]
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
            <a class="btn btn-light" href="{paths["websites"]}">{esc(t["cta_web"])} <span class="arrow" aria-hidden="true">→</span></a>
            <a class="btn btn-outline-light" href="{GUIDE_EARLY_URL}" rel="noopener">{esc(t["cta_guide"])}</a>
          </div>
          <p class="hero-sub">{esc(t["web_line"])}</p>
          <div class="hero-links">
            <a href="{esc(SUBSCRIBE_URL)}" rel="noopener">{esc(t["cta_news"])}</a>
            <a href="{paths["templates"]}">{esc(t["link_tpl"])}</a>
            <a href="{JOURNAL_URL}" rel="noopener">{esc(t["link_journal"])}</a>
            <a href="{paths["n8n"]}">{esc(t["link_n8n"])}</a>
          </div>
          <p class="hero-note">{esc(t["hero_note"])}</p>
        </div>
        <aside class="ledger" aria-label="{esc(t["offer_title"])}">
          <div class="ledger-head"><strong>{esc(t["offer_title"])}</strong><span>{esc(t["offer_meta"])}</span></div>
          {offer}
          <p class="ledger-foot">{esc(t["offer_foot"])} <a href="{paths["websites"]}">{esc(t["offer_link"])}</a></p>
        </aside>
      </section>

      <section class="section" id="build-in-public">
        <div class="section-head">
          <div>
            <p class="kicker">{esc(t["bip_kicker"])}</p>
            <h2>{esc(t["bip_title"])}</h2>
            <p>{esc(t["bip_text"])}</p>
          </div>
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
            "<strong>#ad / Anzeige</strong>. This is a sourced tool recommendation, not financial advice."
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
        "s5": "Affiliate programmes — official terms, for context",
        "aff_intro": "Both vendors have an official partner programme. The rates below are the vendors’ published figures.",
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
            "We describe the official terms; we do not treat them as a personal earnings forecast."
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
            "diese werden als <strong>#ad / Anzeige</strong> gekennzeichnet. Das ist eine quellenbelegte Tool-Empfehlung, keine Finanzberatung."
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
        "s5": "Affiliate-Programme — offizielle Konditionen, zur Einordnung",
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
            "Wir geben die offiziellen Konditionen wieder und machen daraus keine eigene Ertragsprognose."
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
            f"Sources checked on {PRUEF_EN}. {N_TOOLS} entries, n8n first. "
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
        "note": "Prices can change. Check the official page before you buy.",
        "machine": "A machine-readable copy of this directory is at /tools.json. A short site map for language models is at /llms.txt.",
    },
    "de": {
        "title": "Automatisierungs- und KI-Agenten-Tools — quellenbelegtes Verzeichnis",
        "description": f"Quellenbelegtes Verzeichnis mit {N_TOOLS} Automatisierungs- und KI-Agenten-Tools. Preise aus offiziellen öffentlichen Seiten vom {PRUEF}.",
        "h1": "Verzeichnis für Automatisierungs- und KI-Agenten-Tools",
        "lede": (
            f"Quellenstand: {PRUEF}. {N_TOOLS} Einträge, n8n zuerst. "
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
        "note": "Preise können sich ändern. Vor einem Kauf die offizielle Seite prüfen.",
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
            f"Product buttons on the n8n recommendation go to the official n8n site "
            f"(N8N_AFFILIATE_URL in config.js is empty; there are no active affiliate links). "
            f"Source date for prices: {PRUEF_EN}."
        ),
        "ad": (
            "Some links on this site may be affiliate links. Those are labelled #ad / Anzeige. "
            "There are currently no active affiliate links."
        ),
        "privacy": (
            "Privacy: this is a static website. We do not use cookies, tracking pixels or analytics, "
            "and we do not collect personal data through this site, except the optional contact form described below. The directory search runs only in your browser. "
            "Links to vendor sites lead directly to those providers. "
            "Exception: if you use the contact form on the Websites pages, your name, email and message are delivered to our inbox by FormSubmit (formsubmit.co). "
            "We use them only to answer your enquiry."
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
            f"Die Produkt-Buttons auf der n8n-Empfehlung führen auf die offizielle n8n-Seite "
            f"(N8N_AFFILIATE_URL in config.js ist leer; es sind keine Affiliate-Links aktiv). "
            f"Quellenstand der Preise: {PRUEF}."
        ),
        "ad": (
            "Einige Links auf dieser Website können Affiliate-Links sein. Diese werden als #ad / Anzeige gekennzeichnet. "
            "Derzeit sind keine Affiliate-Links aktiv."
        ),
        "privacy": (
            "Datenschutz: Dies ist eine statische Website. Wir verwenden keine Cookies, Tracking-Pixel oder Analysedienste "
            "und erheben über diese Seite keine personenbezogenen Daten, außer über das unten beschriebene freiwillige Kontaktformular. Die Suche im Verzeichnis läuft nur in Ihrem Browser. "
            "Links zu Anbieterseiten führen unmittelbar dorthin. "
            "Ausnahme: Wenn Sie das Kontaktformular auf den Websites-Seiten nutzen, werden Name, E-Mail und Nachricht über FormSubmit (formsubmit.co) an unser Postfach zugestellt. "
            "Wir nutzen diese Angaben nur zur Beantwortung Ihrer Anfrage."
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
          <p>We write about the websites, templates and tools we are building in Lisbon in the Desire Agency newsletter.</p>
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
<html lang="en" data-theme="dark">
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
        "affiliate_links_active": False,
        "n_entries": N_TOOLS,
        "note": (
            "Prices come only from official public vendor pages on the checked date. "
            "Where a figure was not reliably readable, price_status is unknown or partial. "
            "There are no active affiliate links on this site. "
            "Prices can change; check the official page before you buy."
        ),
        "note_de": (
            "Preise nur aus offiziellen öffentlichen Anbieterseiten vom Prüfdatum. "
            "Wo ein Betrag nicht zuverlässig ablesbar war, ist price_status unbekannt oder teilweise. "
            "Auf dieser Seite sind keine Affiliate-Links aktiv. "
            "Preise können sich ändern; prüfe die offizielle Seite vor dem Kauf."
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
Products: Agent Team Guide ({GUIDE_URL}, $19), free Trading Journal + Risk Sheet ({JOURNAL_URL}).
Elsewhere: X {X_URL} · dev.to {DEVTO_URL} · Indie Hackers {IH_URL}.
There are no active affiliate links. Future affiliate links, if any, will be labelled #ad / Anzeige.
This is a static site with no cookies, tracking or analytics.

## Pages

- [Home (English)]({SITE_URL}/): Desire Agency, websites for small businesses from Lisbon, built with an AI agent team. Packages Vitrine, Atelier and Maison (payment after completion), products (Agent Team Guide, free trading journal, free n8n templates), why we recommend n8n, and sourced cloud-pricing facts as of {PRUEF_EN}.
- [Home (German)]({SITE_URL}/de/): The same start page in German.
- [n8n recommendation (English)]({SITE_URL}/n8n/): Sourced article on n8n, self-hosting, and a fair comparison with Make. Buttons go to the official n8n site.
- [n8n recommendation (German)]({SITE_URL}/de/n8n/): The same article in German.
- [Tool directory (English)]({SITE_URL}/directory/): {N_TOOLS} sourced entries (n8n listed first). Each entry has a short description, official and pricing URLs, and a price field. Where a figure was not reliably readable, it is marked unknown. schema.org JSON-LD (ItemList of SoftwareApplication) is embedded in the page.
- [Tool directory (German)]({SITE_URL}/de/directory/): The same directory in German, with the same JSON-LD in German wording.
- [Free n8n templates (English)]({SITE_URL}/templates/): Three free, importable n8n workflows (RSS digest email, form to Google Sheet, website uptime alert with a 60-second retry before the alert). Each section has setup steps and a download link to workflow.json. Credentials in the files are placeholders only. There is no German version of this page.
- [Legal notice / Impressum (English)]({SITE_URL}/legal/): Operator, address, contact, advertising note, and privacy (static site, no cookies or tracking).
- [Legal notice / Impressum (German)]({SITE_URL}/de/legal/): The same legal notice in German.
- [Websites (English)]({SITE_URL}/websites/): Website service for small businesses: Vitrine (one page) from €390, Atelier (3–5 pages) from €750, Maison (up to 8 pages, two languages) from €1,190, Care €29/month. Final prices. No VAT charged – exempt under Art. 53 CIVA (Portugal). Delivery times count from the complete briefing. Enquiries by contact form (delivered via FormSubmit) or email; no online payment. Payment after completion, no deposit.
- [Websites (German)]({SITE_URL}/de/websites/): The same service page in German.
- [Websites (European Portuguese)]({SITE_URL}/pt/websites/): The same service page in Portuguese (pt-PT). "Preços finais. IVA isento ao abrigo do artigo 53.º do CIVA."
- [Demos]({SITE_URL}/demos/): Six example sites for fictional small businesses (Lisbon barbearia, bilingual tasca, Christmas campaign tasca, sapateiro; Dublin café; Bristol handyman), clearly labelled as demos.
- [Desire Agency newsletter]({SUBSCRIBE_URL}): Sign-up page for the free “build log” newsletter.

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
        ("/pt/websites/", "0.9", "weekly"),
        ("/demos/", "0.6", "weekly"),
        ("/llms.txt", "0.5", "weekly"),
        ("/tools.json", "0.6", "weekly"),
    ]
    lastmod_default = "2026-11-21"
    lastmod_today = "2026-11-26"
    urls = []
    for path, prio, freq in paths:
        lastmod = lastmod_today if path in ("/", "/de/", "/n8n/", "/de/n8n/", "/templates/", "/directory/", "/de/directory/", "/legal/", "/de/legal/", "/websites/", "/de/websites/", "/pt/websites/", "/demos/", "/llms.txt", "/tools.json") else lastmod_default
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
        (ROOT / "pt" / "websites" / "index.html", "pt", "websites", 2, WEBSITES["pt"], lambda lang, paths=None: websites_body(lang)),
    ]
    for path, lang, page, depth, meta, body_fn in pages:
        paths = page_paths(lang, depth)
        if page == "home":
            body = body_fn(lang, paths)
        else:
            body = body_fn(lang)
        extra_head = directory_jsonld(lang) if page == "directory" else ""
        html_out = split_h1(shell(lang, page, depth, meta["title"], meta["description"], body, extra_head=extra_head))
        write(path, html_out)
    write(ROOT / "404.html", not_found())
    # /pt/ has no own home page yet: send visitors to the Portuguese service page instead of a 404.
    write(ROOT / "pt" / "index.html", """<!doctype html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Desire Agency – Sites para pequenos negócios</title>
  <meta name="robots" content="noindex, follow">
  <link rel="canonical" href="https://maximussoroka.github.io/pt/websites/">
  <meta http-equiv="refresh" content="0; url=websites/">
  <script>location.replace("websites/" + location.search + location.hash);</script>
</head>
<body><p><a href="websites/">Sites para pequenos negócios – Desire Agency</a></p></body>
</html>
""")
    write(ROOT / GSC_FILE, f"google-site-verification: {GSC_FILE}")
    import demos as _demos
    for rel, html_doc in _demos.pages(SITE_URL).items():
        write(ROOT / rel, html_doc)
    write_public_tools_json()
    write_llms_txt()
    write_sitemap()
    write_robots()
    print(f"done. {N_TOOLS} tools, languages en+de, plus /templates/. Wrote llms.txt, tools.json, sitemap.xml, robots.txt.")


if __name__ == "__main__":
    build()
