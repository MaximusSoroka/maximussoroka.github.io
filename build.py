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
        ("legal", "Legal notice"),
    ],
    "de": [
        ("home", "Start"),
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


def shell(lang: str, page: str, depth: int, title: str, description: str, body: str, extra_js: str = "", extra_head: str = "") -> str:
    paths = page_paths(lang, depth)
    nav = []
    for key, label in NAV[lang]:
        href = paths[key]
        cur = ' aria-current="page"' if key == page else ""
        nav.append(f'<a href="{href}"{cur}>{esc(label)}</a>')
    other = "Deutsch" if lang == "en" else "English"
    other_href = lang_href(lang, page, depth)
    en_cur = ' aria-current="true"' if lang == "en" else ""
    de_cur = ' aria-current="true"' if lang == "de" else ""
    wrap = "wrap-narrow" if page in ("n8n", "legal", "home", "templates") else "wrap"
    # home uses wrap for facts; keep wrap-narrow for typography? I'll use wrap on home.
    if page == "home" or page == "directory":
        wrap = "wrap"
    dir_js = f'\n<script src="{paths["js_dir"]}" defer></script>' if page == "directory" else ""
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index, follow">
  <meta name="description" content="{esc(description)}">
  <title>{esc(title)}</title>
  <link rel="stylesheet" href="{paths['css']}">
{extra_head}</head>
<body>
  <a class="skip" href="#content">{"Skip to content" if lang == "en" else "Zum Inhalt"}</a>
  <header class="site-header">
    <div class="header-inner {wrap}">
      <a class="brand" href="{paths['home']}">
        <span class="brand-name">Desire Agency</span>
        <span class="brand-tag">{"Automation tools, sourced" if lang == "en" else "Automatisierungs-Tools, mit Quellen"}</span>
      </a>
      <nav aria-label="{"Main" if lang == "en" else "Hauptnavigation"}">
        {''.join(nav)}
        <span class="lang" aria-label="Language">
          <a href="{other_href if lang == "de" else "#"}"{en_cur}>EN</a>
          <a href="{other_href if lang == "en" else "#"}"{de_cur}>DE</a>
        </span>
      </nav>
    </div>
  </header>
  <div class="ad-banner">
    <div class="{wrap}">{BANNER[lang]}</div>
  </div>
  <main id="content">
    <div class="{wrap}">
{body}
    </div>
  </main>
  <footer class="site-footer">
    <div class="{wrap}">
      <p>{esc(FOOT[lang])}</p>
      <p>
        <a href="{paths['legal']}">{"Legal notice / Impressum" if lang == "en" else "Impressum / Kontakt"}</a>
        · <a href="{esc(SUBSCRIBE_URL)}">{esc(SUBSCRIBE_LABEL[lang])}</a>
        · <a href="{other_href}">{other}</a>
      </p>
    </div>
  </footer>
  <script src="{paths['config']}"></script>
  <script src="{paths['js_aff']}"></script>{dir_js}{extra_js}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

HOME = {
    "en": {
        "title": "Why we recommend n8n — Desire Agency",
        "description": "An honest, sourced recommendation of n8n, and a directory of 19 automation and AI-agent tools. Prices checked 18 November 2026.",
        "h1": "Why we recommend n8n",
        "lede": "And when Make is still a fair fit. An honest, sourced guide to automation and agent workflows. No earnings promises. Sources checked on 18 November 2026.",
        "cta1": "Read the recommendation",
        "cta2": "Browse 19 tools",
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
        "tpl_title": "Free n8n templates",
        "tpl_text": "Three small, free n8n workflows you can import and adapt: a daily RSS digest, a form that writes to Google Sheets, and an uptime check that retries once after 60 seconds before alerting. Credentials in the files are placeholders.",
        "tpl_cta": "Open the templates",
    },
    "de": {
        "title": "Warum wir n8n empfehlen — Desire Agency",
        "description": "Eine ehrliche, quellenbelegte Empfehlung für n8n und ein Verzeichnis mit 19 Automatisierungs- und KI-Agenten-Tools. Preise geprüft am 18.11.2026.",
        "h1": "Warum wir n8n empfehlen",
        "lede": "Und wann Make trotzdem passt. Ein ehrlicher, quellenbelegter Text zu Automatisierung und Agenten-Workflows. Kein Gewinnversprechen. Quellenstand: 18.11.2026.",
        "cta1": "Empfehlung lesen",
        "cta2": "19 Tools ansehen",
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
        "tpl_title": "Kostenlose n8n-Vorlagen",
        "tpl_text": "Drei kleine, kostenlose n8n-Workflows zum Importieren: ein täglicher RSS-Digest, ein Formular in Google Sheets und eine Erreichbarkeitsprüfung, die nach 60 Sekunden einmal erneut prüft, bevor sie alarmiert. Die Dateien enthalten nur Platzhalter für Zugangsdaten. Die Seite ist auf Englisch.",
        "tpl_cta": "Zu den Vorlagen",
    },
}


def home_body(lang: str, paths: dict) -> str:
    t = HOME[lang]
    facts = "\n".join(
        f'<article class="fact"><h3>{esc(h)}</h3><p>{esc(p)}</p></article>'
        for h, p in t["facts"]
    )
    return f"""
      <section class="hero">
        <h1>{esc(t["h1"])}</h1>
        <p class="lede">{esc(t["lede"])}</p>
        <div class="actions">
          <a class="btn btn-primary" href="{paths["n8n"]}">{esc(t["cta1"])}</a>
          <a class="btn btn-ghost" href="{paths["directory"]}">{esc(t["cta2"])}</a>
          <a class="btn btn-ad" data-aff="n8n" href="https://n8n.io/">{esc(t["cta_n8n"])}</a>
        </div>
        <p class="aff-state" data-aff-state="n8n"></p>
      </section>
      <section class="section">
        <h2>{esc(t["facts_title"])}</h2>
        <div class="facts">{facts}</div>
      </section>
      <section class="section">
        <h2>{esc(t["dir_title"])}</h2>
        <p>{esc(t["dir_text"])}</p>
        <div class="actions"><a class="btn btn-ghost" href="{paths["directory"]}">{esc(t["dir_cta"])}</a></div>
        <p class="note">{esc(t["rev"])}</p>
      </section>
      <section class="section">
        <h2>{esc(t["tpl_title"])}</h2>
        <p>{esc(t["tpl_text"])}</p>
        <div class="actions"><a class="btn btn-ghost" href="{paths["templates"]}">{esc(t["tpl_cta"])}</a></div>
      </section>
      <section class="section">
        <h2>{esc(t["news_title"])}</h2>
        <p>{esc(t["news_text"])}</p>
        <div class="actions"><a class="btn btn-primary" href="{esc(SUBSCRIBE_URL)}">{esc(t["news_cta"])}</a></div>
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
      <h1 class="page-title">{esc(t["h1"])}</h1>
      <p class="lede">{esc(t["lead"])}</p>
      <dl class="placeholder-box">{fields}</dl>
      <p>{esc(t["status"])}</p>
      <p>{esc(t["ad"])}</p>
      <h2>{"Privacy" if lang == "en" else "Datenschutz"}</h2>
      <p>{esc(t["privacy"])}</p>
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
        <section class="section" id="{esc(t['id'])}">
          <h2>{esc(t['title'])}</h2>
          <p>{esc(t['summary'])}</p>
          <div class="actions">
            <a class="btn btn-primary" href="{esc(t['file'])}" download>Download workflow.json</a>
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
  <link rel="stylesheet" href="css/site.css">
</head>
<body>
  <main class="wrap-narrow" style="padding:3rem 0">
    <h1>Page not found</h1>
    <p>This URL is not part of the site. / Diese Adresse gehört nicht zur Seite.</p>
    <p><a href="./">Home (English)</a> · <a href="./de/">Start (Deutsch)</a></p>
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
There are no active affiliate links. Future affiliate links, if any, will be labelled #ad / Anzeige.
This is a static site with no cookies, tracking or analytics.

## Pages

- [Home (English)]({SITE_URL}/): Why we recommend n8n, and when Make may still be a fair fit. Sourced cloud-pricing facts as of {PRUEF_EN}.
- [Home (German)]({SITE_URL}/de/): The same start page in German.
- [n8n recommendation (English)]({SITE_URL}/n8n/): Sourced article on n8n, self-hosting, and a fair comparison with Make. Buttons go to the official n8n site; the n8n partner application was declined on 19 November 2026.
- [n8n recommendation (German)]({SITE_URL}/de/n8n/): The same article in German.
- [Tool directory (English)]({SITE_URL}/directory/): {N_TOOLS} sourced entries (n8n listed first). Each entry has a short description, official and pricing URLs, and a price field. Where a figure was not reliably readable, it is marked unknown. schema.org JSON-LD (ItemList of SoftwareApplication) is embedded in the page.
- [Tool directory (German)]({SITE_URL}/de/directory/): The same directory in German, with the same JSON-LD in German wording.
- [Free n8n templates (English)]({SITE_URL}/templates/): Three free, importable n8n workflows (RSS digest email, form to Google Sheet, website uptime alert with a 60-second retry before the alert). Each section has setup steps and a download link to workflow.json. Credentials in the files are placeholders only. There is no German version of this page.
- [Legal notice / Impressum (English)]({SITE_URL}/legal/): Operator, address, contact, advertising note, and privacy (static site, no cookies or tracking).
- [Legal notice / Impressum (German)]({SITE_URL}/de/legal/): The same legal notice in German.
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
        ("/llms.txt", "0.5", "weekly"),
        ("/tools.json", "0.6", "weekly"),
    ]
    lastmod = "2026-11-20"
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
