"""Demo sites for fictional small businesses. Imported by build.py.

All businesses, names, addresses, phone numbers, prices, hours and reviews are invented.
Photos: CC0 (StockSnap.io), compressed to WebP and wrapped in SVG (text-only repo pushes), see demos/credits.txt.
Fonts: Google Fonts (SIL Open Font License), latin subset, base64-inlined from demos/assets/fonts/*.css.
No external requests, no JavaScript, no frameworks.
"""
from __future__ import annotations
from html import escape as _e

# ------------------------------------------------------------------ assets
IMG = {  # (width, height) of generated images (WebP inside SVG wrapper)
    "barbearia": {"hero": (960, 637), "hero_s": (560, 372)},
    "tasca": {"hero": (960, 638), "hero_s": (560, 372)},
    "sapateiro": {"hero": (960, 638), "hero_s": (560, 372)},
    "handyman": {"hero": (960, 640), "hero_s": (560, 373)},
    "cafe": {"hero": (960, 720), "hero_s": (560, 420)},
}
FONTS = {
    "oswald": ("Oswald", "oswald-500.woff2", "500 600"),
    "fraunces": ("Fraunces", "fraunces-600.woff2", "600"),
    "dmserif": ("DM Serif Display", "dmserif-400.woff2", "400"),
    "barlow": ("Barlow Condensed", "barlow-700.woff2", "700"),
    "youngserif": ("Young Serif", "youngserif-400.woff2", "400"),
}
PKG = {  # name -> (anchor, price text per language). Prices identical to /websites/.
    "Vitrine": ("pkg-vitrine", {"pt": "a partir de 390 €", "en": "from €390", "de": "ab 390 €"}),
    "Atelier": ("pkg-atelier", {"pt": "a partir de 750 €", "en": "from €750", "de": "ab 750 €"}),
    "Maison": ("pkg-maison", {"pt": "a partir de 1190 €", "en": "from €1,190", "de": "ab 1.190 €"}),
}
VAT = {  # verbatim from build.py WEBSITES[...]["vat"]
    "pt": "Preços finais. IVA isento ao abrigo do artigo 53.º do CIVA.",
    "en": "Final prices. No VAT charged – exempt under Art. 53 CIVA (Portugal).",
}


def hero_img(slug: str, alt: str, sizes: str, prefix: str = "") -> str:
    w, h = IMG[slug]["hero"]
    return (f'<img class="hero-img" src="{prefix}img/hero-960.svg" srcset="{prefix}img/hero-560.svg 560w, {prefix}img/hero-960.svg 960w" '
            f'sizes="{sizes}" width="{w}" height="{h}" alt="{_e(alt)}" fetchpriority="high" decoding="async">')


def gallery(alts: list[str], prefix: str = "") -> str:
    return '<div class="gal">' + "".join(
        f'<img src="{prefix}img/g{i}.svg" width="600" height="450" alt="{_e(a)}" loading="lazy" decoding="async">'
        for i, a in enumerate(alts, 1)) + "</div>"


def stars(n: int = 5) -> str:
    return f'<span class="stars" aria-label="{n} de 5">' + "★" * n + "</span>"


def map_svg(c: dict, label: str, street_a: str, street_b: str) -> str:
    """Stylised neighbourhood map (no Google embed = no external request, no cookies)."""
    blocks = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{c["block"]}"/>' for x, y, w, h in [
        (14, 14, 120, 70), (150, 14, 90, 70), (256, 14, 130, 40), (14, 104, 70, 64), (100, 104, 140, 64),
        (256, 70, 130, 98), (14, 188, 160, 58), (190, 188, 196, 58)])
    return f"""<svg class="mapsvg" viewBox="0 0 400 260" role="img" aria-label="{_e(label)}">
<rect width="400" height="260" fill="{c["bg"]}"/>{blocks}
<rect x="256" y="70" width="60" height="98" rx="6" fill="{c["park"]}"/>
<path d="M0 94 H400 M0 178 H400 M142 0 V260 M248 0 V260" stroke="{c["road"]}" stroke-width="10"/>
<path d="M0 260 L400 40" stroke="{c["road"]}" stroke-width="6" opacity=".7"/>
<text x="12" y="90" font-size="10" font-family="system-ui,sans-serif" fill="{c["text"]}">{_e(street_a)}</text>
<text x="150" y="250" font-size="10" font-family="system-ui,sans-serif" fill="{c["text"]}" transform="rotate(-90 150 250)">{_e(street_b)}</text>
<circle cx="195" cy="136" r="22" fill="{c["pin"]}" opacity=".18"/>
<path d="M195 150 c-10-14-16-22-16-30 a16 16 0 1 1 32 0 c0 8-6 16-16 30z" fill="{c["pin"]}"/>
<circle cx="195" cy="120" r="6" fill="{c["bg"]}"/>
</svg>"""


PHONE_SVG = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>'
CHAT_SVG = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.7 14.9L2 22l5.2-1.3A10 10 0 1 0 12 2zm0 18a8 8 0 0 1-4.1-1.1l-.3-.2-3.1.8.8-3-.2-.3A8 8 0 1 1 12 20z"/></svg>'
PIN_SVG = '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg>'

BASE_CSS = """
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:1rem}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;overflow-wrap:break-word}
img{display:block;max-inline-size:100%;block-size:auto}
h1,h2,h3{text-wrap:balance;margin:0}
p,li{text-wrap:pretty}
.wrap{max-width:1140px;margin-inline:auto;padding-inline:clamp(1.15rem,4vw,2.2rem)}
:focus-visible{outline:3px solid currentColor;outline-offset:3px}
.dbar{font:500 12.5px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:#18181b;color:#f4f4f5;padding:.5rem 1rem;text-align:center;position:relative;z-index:40}
.dbar b{font-weight:700;letter-spacing:.06em;text-transform:uppercase;margin-right:.35rem}
.dbar a{color:#fff;text-underline-offset:2px}
.gal{display:grid;grid-template-columns:repeat(2,1fr);gap:.6rem}
@media(min-width:760px){.gal{grid-template-columns:repeat(4,1fr);gap:.8rem}}
.gal img{width:100%;aspect-ratio:4/3;object-fit:cover}
.mapsvg{display:block;width:100%;height:auto}
.hero-img{width:100%;height:100%;object-fit:cover}
.mcta{position:fixed;inset-inline:0;bottom:0;z-index:30;display:flex;gap:.55rem;padding:.6rem max(.75rem,env(safe-area-inset-right,0px)) max(.6rem,env(safe-area-inset-bottom,0px)) max(.75rem,env(safe-area-inset-left,0px))}
.mcta a{flex:1;min-block-size:48px;display:flex;align-items:center;justify-content:center;gap:.45rem;font:700 1rem/1.1 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;text-decoration:none}
@media(min-width:900px){.mcta{display:none}}
@media(max-width:899px){html{scroll-padding-bottom:calc(5rem + env(safe-area-inset-bottom,0px))}body{padding-bottom:calc(4.4rem + env(safe-area-inset-bottom,0px))}}
.agency{background:#18181b;color:#e4e4e7;font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;padding:3.2rem 0 3.6rem}
.agency .wrap{max-width:760px;text-align:center}
.agency .atag{display:inline-block;font-size:.75rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#a1a1aa;border:1px solid #3f3f46;border-radius:999px;padding:.25rem .7rem}
.agency h2{font-size:clamp(1.4rem,3.5vw,1.9rem);color:#fff;margin:.9rem 0 .6rem;font-family:inherit}
.agency p{margin:.35rem auto;color:#d4d4d8;max-width:60ch}
.agency .btns{display:flex;flex-wrap:wrap;gap:.6rem;justify-content:center;margin-top:1.3rem}
.agency .btns a{min-block-size:48px;display:inline-flex;align-items:center;padding:0 1.3rem;border-radius:999px;font-weight:700;text-decoration:none}
.agency .b1{background:#fff;color:#18181b}.agency .b2{border:1px solid #71717a;color:#fff}
.agency small{display:block;margin-top:1.4rem;color:#a1a1aa;font-size:.82rem;line-height:1.7}
.agency small a{color:#e4e4e7}
"""


def font_face(key: str, root: str = "") -> str:
    """Inline the base64 @font-face (demos/assets/fonts/<key>.css) so pages need no extra request."""
    import pathlib
    css = (pathlib.Path(__file__).parent / "demos" / "assets" / "fonts" / f"{key}.css").read_text(encoding="utf-8")
    return "".join(l for l in css.splitlines() if l.startswith("@font-face"))


def demo_bar(lang: str, pkg: str, root: str) -> str:
    anchor = PKG[pkg][0]
    if lang == "pt":
        return (f'<div class="dbar" role="note"><b>Demo</b>Negócio fictício – nomes, contactos, preços e avaliações são inventados. '
                f'Exemplo do pacote <a href="{root}pt/websites/#{anchor}">{pkg}</a> da Desire Agency.</div>')
    return (f'<div class="dbar" role="note"><b>Demo</b>Fictional business – names, contacts, prices and reviews are invented. '
            f'Example of the <a href="{root}websites/#{anchor}">{pkg}</a> package by Desire Agency.</div>')


def agency(lang: str, pkg: str, root: str, what: str) -> str:
    anchor, price = PKG[pkg]
    if lang == "pt":
        return f"""
<section class="agency" aria-label="Desire Agency">
  <div class="wrap">
    <span class="atag">Exemplo / demo – negócio fictício</span>
    <h2>Quer um site assim para o seu negócio?</h2>
    <p>{what} Esta demo corresponde ao pacote <strong>{pkg}</strong>, {price[lang]}.</p>
    <p>{VAT["pt"]} Pagamento só após conclusão.</p>
    <div class="btns"><a class="b1" href="{root}pt/websites/#{anchor}">Ver o pacote {pkg} →</a><a class="b2" href="{root}pt/websites/#contacto">Pedir orçamento</a></div>
    <small>Fotografias CC0 (StockSnap.io), tipos de letra SIL OFL – <a href="{root}demos/credits.txt">créditos</a> · <a href="{root}demos/">Todas as demos</a> · Also in <a href="{root}websites/#{anchor}">English</a> · Auf <a href="{root}de/websites/#{anchor}">Deutsch</a></small>
  </div>
</section>"""
    return f"""
<section class="agency" aria-label="Desire Agency">
  <div class="wrap">
    <span class="atag">Example / demo – fictional business</span>
    <h2>Want a site like this for your business?</h2>
    <p>{what} This demo matches our <strong>{pkg}</strong> package, {price["en"]}.</p>
    <p>{VAT["en"]} Payment after completion, no deposit.</p>
    <div class="btns"><a class="b1" href="{root}websites/#{anchor}">See the {pkg} package →</a><a class="b2" href="{root}websites/#contacto">Ask for a quote</a></div>
    <small>Photos CC0 (StockSnap.io), fonts SIL OFL – <a href="{root}demos/credits.txt">credits</a> · <a href="{root}demos/">All demos</a> · Em <a href="{root}pt/websites/#{anchor}">português</a> · Auf <a href="{root}de/websites/#{anchor}">Deutsch</a></small>
  </div>
</section>"""


def doc(*, lang: str, title: str, desc: str, canon: str, theme: str, font: str, root: str, css: str,
        body: str, pkg: str, what: str, preload_hero: str, alternates: str = "") -> str:
    html_lang = {"pt": "pt-PT", "en": "en-GB"}[lang]
    label = "demo – negócio fictício" if lang == "pt" else "demo – fictional business"
    fam, fn, _ = FONTS[font]
    return f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="robots" content="noindex, follow">
  <title>{_e(title)} ({label})</title>
  <meta name="description" content="{_e(desc)}">
  <link rel="canonical" href="{canon}">{alternates}
  <meta name="theme-color" content="{theme}">
  <link rel="icon" href="{root}favicon.svg" type="image/svg+xml">
  <link rel="preload" as="image" href="{preload_hero}img/hero-960.svg" imagesrcset="{preload_hero}img/hero-560.svg 560w, {preload_hero}img/hero-960.svg 960w" imagesizes="(min-width:900px) 50vw, 100vw" fetchpriority="high">
  <style>{font_face(font, root)}{BASE_CSS}{css}</style>
</head>
<body>
{demo_bar(lang, pkg, root)}
{body}
{agency(lang, pkg, root, what)}
</body>
</html>
"""


# ================================================================== barbearia (PT, Vitrine)
BARBER_CSS = """
body{background:#121110;color:#ece6dc;font:17px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
h1,h2,h3,.logo,.eyebrow,.btn,.mcta a{font-family:"Oswald","Arial Narrow",system-ui,sans-serif;font-size-adjust:cap-height from-font}
a{color:#d8b26a}
.nav{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding-block:1rem;border-bottom:1px solid #2b2722}
.logo{font-weight:600;font-size:1.25rem;letter-spacing:.14em;text-transform:uppercase;color:#ece6dc;text-decoration:none;line-height:1.1}
.logo span{display:block;font:500 .7rem/1.4 system-ui,sans-serif;letter-spacing:.24em;color:#a89f90}
.nav ul{display:none;list-style:none;margin:0;padding:0;gap:1.6rem}
.nav ul a{color:#cfc7b8;text-decoration:none;font-size:.95rem}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;min-block-size:48px;padding:0 1.4rem;background:#d8b26a;color:#16130f;font-weight:600;font-size:1rem;letter-spacing:.08em;text-transform:uppercase;text-decoration:none;border-radius:2px}
.btn.ghost{background:transparent;color:#ece6dc;border:1px solid #5b5246}
.nav .btn{display:none}
.hero{display:grid;gap:1.6rem;padding-block:0 3.5rem}
.hero-media{position:relative;aspect-ratio:4/3;order:-1;margin-inline:calc(-1*clamp(1.15rem,4vw,2.2rem))}
.hero-media::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent 55%,#121110)}
.eyebrow{color:#d8b26a;font-size:.85rem;letter-spacing:.28em;text-transform:uppercase}
.hero h1{font-size:clamp(2.6rem,9vw,5.2rem);line-height:.98;font-weight:600;text-transform:uppercase;margin:.6rem 0 1rem;letter-spacing:.01em}
.hero h1 em{font-style:normal;color:#d8b26a}
.hero .eyebrow{color:#d8b26a;margin:0}
.hero p{color:#c8c0b2;max-width:38ch;margin:0 0 1.6rem;font-size:1.08rem}
.cta-row{display:flex;flex-wrap:wrap;gap:.7rem}
.facts{display:grid;grid-template-columns:repeat(3,1fr);border-block:1px solid #2b2722;margin-top:2.2rem}
.facts div{padding:1rem .4rem;text-align:center;font-size:.85rem;color:#a89f90}
.facts div+div{border-left:1px solid #2b2722}
.facts b{display:block;font:600 1.35rem/1.2 "Oswald",system-ui,sans-serif;color:#ece6dc}
section.s{padding-block:4rem;border-top:1px solid #2b2722}
.s h2{font-size:clamp(2rem,5vw,3rem);text-transform:uppercase;font-weight:600;line-height:1;margin-bottom:.5rem}
.s .lead{color:#a89f90;margin:0 0 2rem}
.menu{display:grid;gap:0 3rem}
.item{display:grid;grid-template-columns:1fr auto;align-items:baseline;gap:.2rem 1rem;padding:1rem 0;border-bottom:1px solid #2b2722}
.item h3{font-size:1.25rem;font-weight:500;letter-spacing:.04em;text-transform:uppercase}
.item .p{font:600 1.35rem "Oswald",system-ui,sans-serif;color:#d8b26a}
.item small{grid-column:1/-1;color:#a89f90;font-size:.92rem}
.note{font-size:.85rem;color:#8f8677;margin-top:1.2rem}
.reviews{display:grid;gap:1rem}
.rev{background:#1b1916;border:1px solid #2b2722;padding:1.4rem;margin:0}
.rev blockquote{margin:.6rem 0 1rem;font-size:1.05rem;color:#e2dbcf}
.rev figcaption{font-size:.9rem;color:#a89f90}
.stars{color:#d8b26a;letter-spacing:.15em}
.visit{display:grid;gap:2rem}
.hours{width:100%;border-collapse:collapse}
.hours th,.hours td{padding:.7rem 0;border-bottom:1px solid #2b2722;text-align:left;font-weight:400}
.hours td{text-align:right;color:#ece6dc}
.hours th{color:#c8c0b2}
.today{color:#d8b26a!important}
.contact p{margin:.2rem 0 1rem;color:#c8c0b2}
.contact b{color:#ece6dc;font-weight:600}
.map{border:1px solid #2b2722}
.maplink{display:inline-flex;align-items:center;gap:.4rem;min-block-size:44px;margin-top:.6rem}
footer.f{padding:2rem 0;border-top:1px solid #2b2722;color:#8f8677;font-size:.85rem}
.mcta{background:rgba(18,17,16,.94);border-top:1px solid #2b2722;backdrop-filter:blur(8px)}
.mcta a{background:#d8b26a;color:#16130f;letter-spacing:.08em;text-transform:uppercase;border-radius:2px}
.mcta a.alt{background:transparent;color:#ece6dc;border:1px solid #5b5246}
@media(min-width:900px){
 .nav ul{display:flex}.nav .btn{display:inline-flex}
 .hero{grid-template-columns:1.05fr 1fr;align-items:center;padding-block:4rem 5rem}
 .hero-media{order:0;margin:0;aspect-ratio:4/5}
 .hero-media::after{background:linear-gradient(90deg,#121110 0,transparent 25%)}
 .menu{grid-template-columns:1fr 1fr}
 .reviews{grid-template-columns:repeat(3,1fr)}
 .visit{grid-template-columns:1fr 1fr 1.2fr}
}
"""


def barbearia(site: str) -> str:
    root = "../../"
    svc = [("Corte clássico", "Tesoura e máquina, lavagem incluída · 30 min", "14 €"),
           ("Barba à navalha", "Toalha quente, óleo e bálsamo · 25 min", "12 €"),
           ("Corte + barba", "O ritual completo · 50 min", "24 €"),
           ("Fade / degradê", "Acabamento à navalha · 40 min", "16 €"),
           ("Corte criança", "Até aos 12 anos · 25 min", "10 €"),
           ("Pai & filho", "Dois cortes, uma cadeira de cada vez", "22 €")]
    items = "".join(f'<div class="item"><h3>{n}</h3><span class="p">{p}</span><small>{d}</small></div>' for n, d, p in svc)
    revs = [("Marquei ao meio-dia pelo WhatsApp e às seis estava sentado. Melhor degradê que tive em Lisboa.", "Tiago R."),
            ("Barba à navalha com toalha quente – saí outra pessoa. Ambiente calmo, sem pressas.", "Miguel A."),
            ("Levo o meu filho desde os 5 anos. Paciência infinita e preço justo.", "Paulo S.")]
    rv = "".join(f'<figure class="rev">{stars()}<blockquote>“{t}”</blockquote><figcaption>{a} · avaliação fictícia</figcaption></figure>' for t, a in revs)
    hours = [("Segunda", "Fechado"), ("Terça – Sexta", "10:00 – 20:00"), ("Sábado", "09:00 – 18:00"), ("Domingo", "Fechado")]
    hr = "".join(f"<tr><th scope=\"row\">{d}</th><td>{h}</td></tr>" for d, h in hours)
    body = f"""
<header class="wrap nav">
  <a class="logo" href="#top" aria-label="Navalha d'Ouro, início">Navalha d'Ouro<span>Barbearia · Arroios</span></a>
  <nav aria-label="Secções"><ul><li><a href="#servicos">Serviços</a></li><li><a href="#galeria">Galeria</a></li><li><a href="#avaliacoes">Avaliações</a></li><li><a href="#visitar">Horário</a></li></ul></nav>
  <a class="btn" href="#marcar">Marcar</a>
</header>
<main id="top">
<section class="wrap hero">
  <div>
    <p class="eyebrow">Barbearia em Arroios · desde 2012</p>
    <h1>Corte clássico. <em>Barba à navalha.</em> Sem pressa.</h1>
    <p>Três cadeiras, toalha quente e boa conversa. Marque pelo WhatsApp em 30 segundos – respondemos no próprio dia.</p>
    <div class="cta-row"><a class="btn" href="#marcar">{CHAT_SVG} Marcar pelo WhatsApp</a><a class="btn ghost" href="#servicos">Ver preços</a></div>
    <div class="facts"><div><b>14 €</b>corte clássico</div><div><b>Ter–Sáb</b>até às 20h</div><div><b>3 min</b>do metro Arroios</div></div>
  </div>
  <div class="hero-media">{hero_img("barbearia", "Cadeira de barbeiro clássica em couro vermelho junto à bancada com navalhas e pincéis", "(min-width:900px) 50vw, 100vw")}</div>
</section>
<section class="s wrap" id="servicos">
  <h2>Serviços &amp; preços</h2><p class="lead">Preço fixo, sem surpresas. Pagamento em dinheiro, cartão ou MB WAY.</p>
  <div class="menu">{items}</div>
  <p class="note">Preços de exemplo – negócio fictício.</p>
</section>
<section class="s wrap" id="galeria" aria-labelledby="gal-h">
  <h2 id="gal-h">O espaço</h2><p class="lead">Ferramentas de sempre, tratadas com cuidado.</p>
  {gallery(["Taça de barbear em metal com pincel e navalhas sobre a bancada", "Tesouras penduradas na parede de madeira", "Barbeiro a cortar o cabelo de um cliente na cadeira", "Barba a ser aparada à navalha"])}
</section>
<section class="s wrap" id="avaliacoes">
  <h2>O que dizem</h2><p class="lead">Avaliações de exemplo, fictícias. No seu site mostramos as avaliações reais do Google, com ligação para o perfil.</p>
  <div class="reviews">{rv}</div>
</section>
<section class="s wrap" id="visitar">
  <h2>Visite-nos</h2><p class="lead">Sem marcação também atendemos – se houver cadeira livre.</p>
  <div class="visit">
    <div><h3 class="eyebrow">Horário</h3><table class="hours">{hr}</table></div>
    <div class="contact" id="marcar"><h3 class="eyebrow">Contactos</h3>
      <p><b>Morada</b><br>Rua Inventada, 00 – Arroios, Lisboa</p>
      <p><b>WhatsApp / telefone</b><br>+351 9XX XXX XXX <small>(fictício)</small></p>
      <p><b>Instagram</b><br>@navalhadouro.demo <small>(fictício)</small></p>
      <a class="btn" href="#marcar">{CHAT_SVG} Marcar agora</a></div>
    <div><div class="map">{map_svg({"bg": "#1b1916", "block": "#26231f", "park": "#24301f", "road": "#3a352e", "pin": "#d8b26a", "text": "#8f8677"}, "Mapa ilustrativo de Arroios com a localização da barbearia", "Av. Almirante Reis", "Rua Inventada")}</div>
      <a class="maplink" href="https://www.google.com/maps/search/?api=1&amp;query=Arroios%2C+Lisboa">{PIN_SVG} Abrir no Google Maps</a></div>
  </div>
</section>
</main>
<footer class="f wrap">© Barbearia Navalha d'Ouro – negócio fictício, criado para demonstração.</footer>
<nav class="mcta" aria-label="Ações rápidas"><a href="#marcar">{CHAT_SVG} Marcar</a><a class="alt" href="#marcar">{PHONE_SVG} Ligar</a></nav>"""
    return doc(lang="pt", title="Barbearia Navalha d'Ouro", desc="Exemplo de site de uma página para uma barbearia em Lisboa (negócio fictício).",
               canon=site + "/demos/barbearia/", theme="#121110", font="oswald", root=root, css=BARBER_CSS, body=body,
               pkg="Vitrine", what="Uma página longa com preços, galeria, avaliações, horário e botão de marcação fixo no telemóvel.",
               preload_hero="")


# ================================================================== tasca (PT + EN, Maison)
TASCA_CSS = """
body{background:#f6f0e4;color:#1e2a3a;font:17px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
h1,h2,h3,.logo,.price{font-family:"Fraunces",Georgia,"Times New Roman",serif;font-size-adjust:from-font}
a{color:#1f4b8e}
.tiles{background-color:#1f4b8e;background-image:radial-gradient(circle at 50% 50%,#f6f0e4 0 5px,transparent 6px),radial-gradient(circle at 0 0,transparent 15px,#f6f0e4 16px 18px,transparent 19px),radial-gradient(circle at 100% 100%,transparent 15px,#f6f0e4 16px 18px,transparent 19px),radial-gradient(circle at 100% 0,transparent 15px,#f6f0e4 16px 18px,transparent 19px),radial-gradient(circle at 0 100%,transparent 15px,#f6f0e4 16px 18px,transparent 19px);background-size:44px 44px}
.strip{height:14px}
.nav{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding-block:1rem}
.logo{font-size:1.35rem;font-weight:600;color:#1f4b8e;text-decoration:none;line-height:1.1}
.logo small{display:block;font:600 .68rem/1.4 system-ui,sans-serif;letter-spacing:.2em;text-transform:uppercase;color:#9e4321}
.nav-r{display:flex;align-items:center;gap:1.2rem}
.nav ul{display:none;list-style:none;margin:0;padding:0;gap:1.4rem}
.nav ul a{text-decoration:none;color:#1e2a3a;font-weight:500}
.lang{display:inline-flex;border:2px solid #1f4b8e;border-radius:999px;overflow:hidden;font-weight:700;font-size:.85rem}
.lang a,.lang span{min-block-size:36px;min-inline-size:44px;display:inline-flex;align-items:center;justify-content:center;padding:0 .7rem;text-decoration:none}
.lang span{background:#1f4b8e;color:#fff}
.hero{display:grid;gap:2rem;padding-block:1.5rem 4rem;align-items:center}
.arch{border-radius:999px 999px 18px 18px;overflow:hidden;aspect-ratio:4/4.4;border:8px solid #fff;box-shadow:0 20px 50px -20px rgba(31,75,142,.45)}
.kicker{font-weight:700;color:#9e4321;letter-spacing:.16em;text-transform:uppercase;font-size:.8rem;margin:0}
.hero h1{font-size:clamp(2.5rem,8vw,4.6rem);line-height:1.02;color:#1f4b8e;margin:.5rem 0 1rem;letter-spacing:-.01em}
.hero h1 i{color:#9e4321}
.hero .kicker{color:#9e4321;margin:0}
.hero p{max-width:40ch;margin:0 0 1.6rem;font-size:1.1rem;color:#33415a}
.btn{display:inline-flex;align-items:center;gap:.5rem;min-block-size:48px;padding:0 1.35rem;border-radius:999px;background:#9e4321;color:#fff;font-weight:700;text-decoration:none}
.btn.o{background:transparent;color:#1f4b8e;border:2px solid #1f4b8e}
.row{display:flex;flex-wrap:wrap;gap:.7rem}
.dia{background:#fff;border-radius:18px;padding:1.4rem 1.5rem;display:grid;gap:.4rem;border:2px dashed #9e4321;max-width:720px;margin-inline:auto;text-align:center}
.dia .kicker{margin-bottom:.2rem}
.dia h2{font-size:clamp(1.5rem,4vw,2rem);color:#1f4b8e}
.dia .price{font-size:1.9rem;color:#9e4321;font-weight:600}
.dia small{color:#5b6476}
section.s{padding-block:4rem}
.s h2{font-size:clamp(2rem,5vw,3rem);color:#1f4b8e;text-align:center;margin-bottom:.4rem}
.s .lead{text-align:center;color:#5b6476;margin:0 auto 2.2rem;max-width:56ch}
.menu{background:#fff;border-radius:22px;padding:clamp(1.2rem,4vw,2.6rem);display:grid;gap:2rem;box-shadow:0 1px 0 #e7dcc6}
.menu h3{font-size:1.35rem;color:#9e4321;margin-bottom:.4rem}
.menu ul{list-style:none;margin:0;padding:0}
.menu li{display:flex;align-items:baseline;gap:.6rem;padding:.55rem 0}
.menu li span{flex:1;border-bottom:1px dotted #b8ad97;transform:translateY(-4px)}
.menu li em{display:block;font-style:normal;font-size:.85rem;color:#5b6476}
.menu b{font-family:"Fraunces",Georgia,serif;font-weight:600;color:#1f4b8e}
.note{text-align:center;font-size:.85rem;color:#5b6476;margin-top:1rem}
.gal img{border-radius:14px}
.reviews{display:grid;gap:1rem}
.rev{background:#fff;border-radius:18px;padding:1.5rem;margin:0;border-top:5px solid #1f4b8e}
.rev blockquote{margin:.5rem 0 .9rem;font-family:"Fraunces",Georgia,serif;font-size:1.15rem;line-height:1.45}
.rev figcaption{color:#5b6476;font-size:.9rem}
.stars{color:#9e4321;letter-spacing:.12em}
.info{display:grid;gap:1rem}
.card{background:#fff;border-radius:18px;padding:1.5rem}
.card h3{color:#1f4b8e;font-size:1.3rem;margin-bottom:.5rem}
.card p{margin:.2rem 0}
.map{border-radius:18px;overflow:hidden;border:6px solid #fff}
.maplink{display:inline-flex;align-items:center;gap:.4rem;min-block-size:44px;font-weight:600}
footer.f{padding:2rem 0 2.4rem;text-align:center;color:#5b6476;font-size:.85rem}
.mcta{background:rgba(246,240,228,.95);border-top:1px solid #e2d6bf;backdrop-filter:blur(8px)}
.mcta a{background:#9e4321;color:#fff;border-radius:999px}
.mcta a.alt{background:#fff;color:#1f4b8e;border:2px solid #1f4b8e}
@media(min-width:900px){
 .nav ul{display:flex}
 .hero{grid-template-columns:1.1fr .9fr;padding-block:3rem 5rem}
 .menu{grid-template-columns:1fr 1fr;column-gap:3.5rem}
 .reviews{grid-template-columns:repeat(3,1fr)}
 .info{grid-template-columns:1fr 1fr 1.3fr}
}
"""

TASCA_TXT = {
    "pt": dict(
        nav=["Ementa", "Galeria", "Avaliações", "Horário"], home="início",
        kicker="Tasca de bairro · Graça, Lisboa", h1="Comida de casa, <i>como a avó fazia.</i>",
        p="Prato do dia ao almoço, petiscos ao jantar e vinho da casa a copo. Doze mesas, uma cozinha pequena e muito sabor.",
        b1="Ligar para reservar", b2="Ver ementa",
        alt="Mesa de madeira posta com pratos brancos, copos e guardanapos numa tasca acolhedora",
        dia_k="Prato do dia · terça", dia="Bacalhau à Brás", dia_d="Com salada e pão · bebida e café incluídos",
        dia_s="O dono muda este texto todas as manhãs no telemóvel, em 1 minuto.",
        menu_h="Ementa", menu_l="Cozinha portuguesa de sempre, com produtos do mercado.",
        cats=[("Petiscos", [("Pica-pau do lombo", "", "8,50 €"), ("Peixinhos da horta", "", "5,00 €"), ("Polvo à galega", "", "9,50 €"), ("Queijo de Azeitão com tostas", "", "7,50 €")]),
              ("Pratos", [("Bitoque com ovo", "Batata frita caseira", "10,50 €"), ("Polvo à lagareiro", "Batata a murro", "17,00 €"), ("Arroz de pato", "No forno", "12,00 €"), ("Sardinhas assadas", "Junho a setembro", "12,50 €")]),
              ("Sobremesas", [("Arroz doce", "", "3,50 €"), ("Baba de camelo", "", "3,50 €"), ("Pastel de nata", "", "1,50 €")]),
              ("Bebidas", [("Vinho da casa (copo)", "Tinto ou branco", "2,50 €"), ("Imperial", "", "1,80 €"), ("Ginjinha", "", "1,50 €")])],
        note="Pratos e preços de exemplo – negócio fictício.",
        gal_h="À mesa", gal_l="Do mercado para a mesa, todos os dias.",
        gal=["Polvo fresco numa travessa de inox", "Tábua de queijos e enchidos com copos de vinho", "Clientes ao balcão com pipas de vinho", "Telhados de Lisboa vistos do miradouro"],
        rev_h="Quem cá vem", rev_l="Avaliações de exemplo, fictícias. No seu site mostramos as avaliações reais do Google.",
        revs=[("O arroz de pato é o melhor da Graça. Pedimos sempre a mesa do canto.", "Ana P."), ("Fomos com amigos estrangeiros e a ementa em inglês ajudou imenso.", "João M."), ("Prato do dia a 11,50 € com café – difícil encontrar melhor no bairro.", "Rita C.")],
        fict="avaliação fictícia",
        vis_h="Horário e reservas", vis_l="Ao fim de semana convém reservar.",
        c1=("Almoço", ["Terça a sábado", "12:00 – 15:00"]), c2=("Jantar", ["Quinta a sábado", "19:30 – 23:00", "Domingo e segunda: fechado"]),
        c3=("Onde estamos", ["Largo Inventado, 00 – Graça, Lisboa", "Elétrico 28, paragem a 2 min", "Reservas: +351 21X XXX XXX (fictício)"]),
        map_l="Mapa ilustrativo da Graça com a localização da tasca", maps="Abrir no Google Maps",
        foot="© Tasca do Pátio Azul – negócio fictício, criado para demonstração.",
        m1="Reservar", m2="Ementa", quick="Ações rápidas",
        title="Tasca do Pátio Azul", desc="Exemplo de site bilingue (PT/EN) para uma tasca em Lisboa (negócio fictício).",
        what="Site bilingue português/inglês para clientes locais e turistas, com prato do dia que o dono atualiza sozinho.",
    ),
    "en": dict(
        nav=["Menu", "Gallery", "Reviews", "Hours"], home="home",
        kicker="Neighbourhood tavern · Graça, Lisbon", h1="Home cooking, <i>just like grandma's.</i>",
        p="Dish of the day at lunch, petiscos (Portuguese tapas) at dinner and house wine by the glass. Twelve tables, a tiny kitchen and lots of flavour.",
        b1="Call to book", b2="See the menu",
        alt="Wooden table set with white plates, glasses and napkins in a cosy tavern",
        dia_k="Dish of the day · Tuesday", dia="Bacalhau à Brás", dia_d="Salt cod, eggs and potato · with salad, bread, a drink and coffee",
        dia_s="The owner updates this text every morning from his phone in one minute.",
        menu_h="Menu", menu_l="Classic Portuguese cooking with produce from the market.",
        cats=[("Petiscos", [("Pica-pau", "Pork strips in garlic sauce", "8,50 €"), ("Peixinhos da horta", "Tempura green beans", "5,00 €"), ("Galician-style octopus", "", "9,50 €"), ("Azeitão cheese with toast", "", "7,50 €")]),
              ("Mains", [("Bitoque", "Steak, egg and home-made chips", "10,50 €"), ("Octopus lagareiro", "Roasted, olive oil and potatoes", "17,00 €"), ("Duck rice", "Oven-baked", "12,00 €"), ("Grilled sardines", "June to September", "12,50 €")]),
              ("Desserts", [("Arroz doce", "Rice pudding", "3,50 €"), ("Baba de camelo", "Caramel mousse", "3,50 €"), ("Pastel de nata", "", "1,50 €")]),
              ("Drinks", [("House wine (glass)", "Red or white", "2,50 €"), ("Draught beer", "", "1,80 €"), ("Ginjinha", "Sour cherry liqueur", "1,50 €")])],
        note="Example dishes and prices – fictional business.",
        gal_h="At the table", gal_l="From the market to your plate, every day.",
        gal=["Fresh octopus on a steel tray", "Cheese and charcuterie board with wine glasses", "Guests at the counter with wine barrels", "Lisbon rooftops seen from a viewpoint"],
        rev_h="What guests say", rev_l="Example reviews, fictional. On your site we show your real Google reviews.",
        revs=[("Best duck rice in Graça. We always ask for the corner table.", "Ana P."), ("The English menu made it so easy for our friends visiting Lisbon.", "Sarah K."), ("Dish of the day for 11,50 € including coffee – hard to beat.", "Tom R.")],
        fict="fictional review",
        vis_h="Hours & bookings", vis_l="Booking recommended at weekends.",
        c1=("Lunch", ["Tuesday to Saturday", "12:00 – 15:00"]), c2=("Dinner", ["Thursday to Saturday", "19:30 – 23:00", "Sunday & Monday: closed"]),
        c3=("Find us", ["Largo Inventado, 00 – Graça, Lisbon", "Tram 28, stop 2 min away", "Bookings: +351 21X XXX XXX (fictional)"]),
        map_l="Illustrated map of Graça showing the tavern", maps="Open in Google Maps",
        foot="© Tasca do Pátio Azul – fictional business, created as a demo.",
        m1="Book", m2="Menu", quick="Quick actions",
        title="Tasca do Pátio Azul", desc="Example bilingual (PT/EN) website for a Lisbon tavern (fictional business).",
        what="A bilingual Portuguese/English site for locals and tourists, with a dish of the day the owner updates himself.",
    ),
}


def tasca(site: str, lang: str = "pt") -> str:
    t = TASCA_TXT[lang]
    en = lang == "en"
    root = "../../../" if en else "../../"
    pre = "../" if en else ""
    sw = ('<span aria-current="true">EN</span>' if en else '<a href="en/" hreflang="en" lang="en">EN</a>')
    sw = (f'<a href="../" hreflang="pt-PT" lang="pt-PT">PT</a>{sw}' if en else f'<span aria-current="true">PT</span>{sw}')
    ids = ["ementa", "galeria", "avaliacoes", "horario"]
    nav = "".join(f'<li><a href="#{i}">{n}</a></li>' for i, n in zip(ids, t["nav"]))
    cats = "".join("<div><h3>" + c + "</h3><ul>" + "".join(
        f'<li><div>{n}{f"<em>{d}</em>" if d else ""}</div><span></span><b>{p}</b></li>' for n, d, p in items) + "</ul></div>" for c, items in t["cats"])
    rv = "".join(f'<figure class="rev">{stars()}<blockquote>“{q}”</blockquote><figcaption>{a} · {t["fict"]}</figcaption></figure>' for q, a in t["revs"])
    card = lambda h, ls: f'<div class="card"><h3>{h}</h3>' + "".join(f"<p>{x}</p>" for x in ls) + "</div>"
    body = f"""
<div class="tiles strip" aria-hidden="true"></div>
<header class="wrap nav">
  <a class="logo" href="#top">Tasca do Pátio Azul<small>Graça · Lisboa</small></a>
  <div class="nav-r"><nav aria-label="{'Sections' if en else 'Secções'}"><ul>{nav}</ul></nav><div class="lang" role="group" aria-label="{'Language' if en else 'Idioma'}">{sw}</div></div>
</header>
<main id="top">
<section class="wrap hero">
  <div>
    <p class="kicker">{t["kicker"]}</p>
    <h1>{t["h1"]}</h1>
    <p>{t["p"]}</p>
    <div class="row"><a class="btn" href="#horario">{PHONE_SVG} {t["b1"]}</a><a class="btn o" href="#ementa">{t["b2"]}</a></div>
  </div>
  <div class="arch">{hero_img("tasca", t["alt"], "(min-width:900px) 45vw, 100vw", pre)}</div>
</section>
<div class="wrap"><div class="dia"><p class="kicker">{t["dia_k"]}</p><h2>{t["dia"]}</h2><p style="margin:0">{t["dia_d"]}</p><span class="price">11,50 €</span><small>{t["dia_s"]}</small></div></div>
<section class="s wrap" id="ementa"><h2>{t["menu_h"]}</h2><p class="lead">{t["menu_l"]}</p>
  <div class="menu">{cats}</div><p class="note">{t["note"]}</p></section>
<div class="tiles strip" aria-hidden="true"></div>
<section class="s wrap" id="galeria"><h2>{t["gal_h"]}</h2><p class="lead">{t["gal_l"]}</p>{gallery(t["gal"], pre)}</section>
<section class="s wrap" id="avaliacoes"><h2>{t["rev_h"]}</h2><p class="lead">{t["rev_l"]}</p><div class="reviews">{rv}</div></section>
<section class="s wrap" id="horario"><h2>{t["vis_h"]}</h2><p class="lead">{t["vis_l"]}</p>
  <div class="info">{card(*t["c1"])}{card(*t["c2"])}
    <div>{card(*t["c3"])}<div class="map" style="margin-top:1rem">{map_svg({"bg": "#eef3fb", "block": "#dbe4f3", "park": "#d6e8cf", "road": "#ffffff", "pin": "#9e4321", "text": "#5b6476"}, t["map_l"], "Rua da Graça", "Largo Inventado")}</div>
    <a class="maplink" href="https://www.google.com/maps/search/?api=1&amp;query=Gra%C3%A7a%2C+Lisboa">{PIN_SVG} {t["maps"]}</a></div>
  </div></section>
</main>
<div class="tiles strip" aria-hidden="true"></div>
<footer class="f wrap">{t["foot"]}</footer>
<nav class="mcta" aria-label="{t["quick"]}"><a href="#horario">{PHONE_SVG} {t["m1"]}</a><a class="alt" href="#ementa">{t["m2"]}</a></nav>"""
    canon = site + ("/demos/tasca/en/" if en else "/demos/tasca/")
    alt = (f'\n  <link rel="alternate" hreflang="pt-PT" href="{site}/demos/tasca/">'
           f'\n  <link rel="alternate" hreflang="en" href="{site}/demos/tasca/en/">')
    return doc(lang=lang, title=t["title"], desc=t["desc"], canon=canon, theme="#1f4b8e", font="fraunces", root=root,
               css=TASCA_CSS, body=body, pkg="Maison", what=t["what"], preload_hero=pre, alternates=alt).replace(
        'imagesizes="(min-width:900px) 50vw, 100vw"', 'imagesizes="(min-width:900px) 45vw, 100vw"')


# ================================================================== sapateiro (PT, Vitrine)
SAPA_CSS = """
body{background:#f2ebe0;color:#241a13;font:17px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
h1,h2,h3,.logo,.num,.tag b{font-family:"DM Serif Display",Georgia,"Times New Roman",serif;font-weight:400;font-size-adjust:from-font}
a{color:#8b4a26}
.nav{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding-block:1.1rem;border-bottom:1px solid #d9ccb8}
.logo{font-size:1.45rem;color:#241a13;text-decoration:none;line-height:1}
.logo small{display:block;font:600 .66rem/1.6 system-ui,sans-serif;letter-spacing:.22em;text-transform:uppercase;color:#8b4a26;margin-top:.2rem}
.nav ul{display:none;list-style:none;margin:0;padding:0;gap:1.5rem}
.nav ul a{text-decoration:none;color:#3d2e22}
.pill{display:inline-flex;align-items:center;gap:.5rem;min-block-size:48px;padding:0 1.3rem;border-radius:999px;background:#3f4a2a;color:#f7f1e6;font-weight:700;text-decoration:none}
.pill.o{background:transparent;color:#241a13;border:1.5px solid #241a13}
.nav .pill{display:none}
.hero{display:grid;gap:2.4rem;padding-block:2.4rem 4rem}
.hero .lbl{font-weight:700;font-size:.8rem;letter-spacing:.18em;text-transform:uppercase;color:#8b4a26;margin:0}
.hero h1{font-size:clamp(2.7rem,9vw,5.4rem);line-height:.98;margin:.6rem 0 1.1rem;letter-spacing:-.015em}
.hero h1 span{color:#8b4a26;font-style:italic}
.hero p{font-size:1.1rem;color:#4a3a2d;max-width:40ch;margin:0 0 1.6rem}
.row{display:flex;flex-wrap:wrap;gap:.7rem}
.frame{position:relative;margin:0 0 1rem 1rem}
.frame::before{content:"";position:absolute;inset:1rem -1rem -1rem 1rem;background:#8b4a26;border-radius:4px;z-index:0;inset:auto;left:-1rem;top:1rem;width:100%;height:100%}
.frame .im{position:relative;z-index:1;aspect-ratio:5/4;border-radius:4px;overflow:hidden}
.stamp{position:absolute;z-index:2;right:-.4rem;bottom:-1.4rem;width:112px;height:112px;border-radius:50%;background:#f2ebe0;border:2px solid #241a13;display:grid;place-items:center;text-align:center;font:700 .72rem/1.25 system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;transform:rotate(-8deg)}
.stamp b{display:block;font:400 1.9rem/1 "DM Serif Display",Georgia,serif;letter-spacing:0;text-transform:none}
section.s{padding-block:4.2rem}
.s.dark{background:#241a13;color:#efe5d6}
.s h2{font-size:clamp(2.1rem,5.5vw,3.3rem);line-height:1.05;margin-bottom:.5rem}
.s .lead{color:#6a5847;max-width:52ch;margin:0 0 2.2rem}
.s.dark .lead{color:#c9b9a3}
.tags{display:grid;gap:1rem}
.tag{position:relative;background:#fffaf2;border:1px solid #e0d3bf;border-radius:6px 22px 22px 6px;padding:1.2rem 1.3rem 1.2rem 1.6rem}
.tag::before{content:"";position:absolute;left:.6rem;top:50%;width:8px;height:8px;margin-top:-4px;border-radius:50%;background:#f2ebe0;border:1.5px solid #b9a789}
.tag h3{font-size:1.35rem}
.tag p{margin:.15rem 0 .5rem;color:#6a5847;font-size:.95rem}
.tag b{font-size:1.5rem;color:#8b4a26}
.tag b small{font:600 .78rem system-ui,sans-serif;color:#6a5847;margin-right:.3rem}
.note{font-size:.85rem;color:#6a5847;margin-top:1rem}
.steps{display:grid;gap:1.4rem;counter-reset:s;list-style:none;margin:0;padding:0}
.steps li{border-top:1px solid #4d3d2f;padding-top:1rem}
.num{font-size:3rem;line-height:1;color:#d49a63}
.steps h3{font-size:1.5rem;margin:.3rem 0}
.steps p{margin:0;color:#c9b9a3}
.gal img{border-radius:4px}
.reviews{display:grid;gap:1.4rem}
.rev{margin:0;padding-left:1.2rem;border-left:3px solid #8b4a26}
.rev blockquote{margin:.4rem 0 .7rem;font:400 1.35rem/1.35 "DM Serif Display",Georgia,serif}
.rev figcaption{font-size:.9rem;color:#6a5847}
.stars{color:#8b4a26;letter-spacing:.12em}
.visit{display:grid;gap:2rem}
.hours{list-style:none;margin:0;padding:0}
.hours li{display:flex;justify-content:space-between;padding:.7rem 0;border-bottom:1px dashed #cbb99f}
.contact p{margin:.2rem 0 1rem}
.map{border-radius:4px;overflow:hidden;border:1px solid #d9ccb8}
.maplink{display:inline-flex;align-items:center;gap:.4rem;min-block-size:44px;font-weight:600}
footer.f{padding:2rem 0;color:#6a5847;font-size:.85rem;border-top:1px solid #d9ccb8}
.mcta{background:rgba(242,235,224,.95);border-top:1px solid #d9ccb8;backdrop-filter:blur(8px)}
.mcta a{background:#3f4a2a;color:#f7f1e6;border-radius:999px}
.mcta a.alt{background:transparent;color:#241a13;border:1.5px solid #241a13}
@media(min-width:700px){.tags{grid-template-columns:1fr 1fr}.steps{grid-template-columns:repeat(3,1fr)}.reviews{grid-template-columns:repeat(3,1fr)}}
@media(min-width:900px){
 .nav ul{display:flex}.nav .pill{display:inline-flex}
 .hero{grid-template-columns:1.05fr 1fr;align-items:center;padding-block:4.5rem 5.5rem}
 .tags{grid-template-columns:repeat(3,1fr)}
 .visit{grid-template-columns:1fr 1fr 1.2fr}
}
"""


def sapateiro(site: str) -> str:
    root = "../../"
    svc = [("Meias-solas", "Couro ou borracha, cosidas ou coladas", "desde", "18 €"),
           ("Tacões", "Senhora e homem, na hora", "desde", "8 €"),
           ("Duplicação de chaves", "Casa, cacifo, gorja e multiponto", "desde", "3 €"),
           ("Fechos de botas", "Substituição completa", "desde", "15 €"),
           ("Costuras e colagens", "Sapatos, malas, cintos", "desde", "6 €"),
           ("Tingir e restaurar couro", "Recupera a cor original", "desde", "20 €")]
    tags = "".join(f'<div class="tag"><h3>{n}</h3><p>{d}</p><b><small>{f}</small>{p}</b></div>' for n, d, f, p in svc)
    steps = [("Envie uma foto", "Pelo WhatsApp, com o que precisa de arranjar."), ("Receba o preço", "Respondemos no mesmo dia útil, sem compromisso."), ("Deixe e levante", "A maioria dos arranjos fica pronta em 48 horas.")]
    st = "".join(f'<li><span class="num">0{i}</span><h3>{h}</h3><p>{p}</p></li>' for i, (h, p) in enumerate(steps, 1))
    revs = [("Umas botas que eu dava como perdidas voltaram como novas. Preço honesto.", "Helena F."),
            ("Mandei foto ao almoço, à tarde já tinha o orçamento. Simples.", "Carlos D."),
            ("Fiz cópia de três chaves em cinco minutos enquanto esperava.", "Sofia L.")]
    rv = "".join(f'<figure class="rev">{stars()}<blockquote>“{q}”</blockquote><figcaption>{a} · avaliação fictícia</figcaption></figure>' for q, a in revs)
    body = f"""
<header class="wrap nav">
  <a class="logo" href="#top">Sapataria Meia-Sola<small>Sapateiro &amp; chaves · Campo de Ourique</small></a>
  <nav aria-label="Secções"><ul><li><a href="#arranjos">Arranjos</a></li><li><a href="#como">Como funciona</a></li><li><a href="#avaliacoes">Avaliações</a></li><li><a href="#contacto">Contacto</a></li></ul></nav>
  <a class="pill" href="#contacto">Pedir orçamento</a>
</header>
<main id="top">
<section class="wrap hero">
  <div>
    <p class="lbl">Sapateiro de bairro · desde 1987</p>
    <h1>Bons sapatos merecem <span>uma segunda vida.</span></h1>
    <p>Meias-solas, tacões, costuras e chaves – feito à mão, no próprio bairro. Mande uma foto e receba o preço no mesmo dia.</p>
    <div class="row"><a class="pill" href="#contacto">{CHAT_SVG} Pedir orçamento por foto</a><a class="pill o" href="#arranjos">Ver preços</a></div>
  </div>
  <div class="frame"><div class="im">{hero_img("sapateiro", "Artesão concentrado na bancada da oficina, com chaves e ferramentas penduradas na parede", "(min-width:900px) 50vw, 100vw")}</div>
    <div class="stamp" aria-hidden="true"><span><b>48 h</b>prontos</span></div></div>
</section>
<section class="s wrap" id="arranjos">
  <h2>Arranjos &amp; preços</h2><p class="lead">O preço final confirma-se ao ver a peça – mas sem surpresas.</p>
  <div class="tags">{tags}</div><p class="note">Preços de exemplo – negócio fictício.</p>
</section>
<section class="s dark" id="como"><div class="wrap">
  <h2>Como funciona</h2><p class="lead">Três passos, sem filas nem telefonemas.</p>
  <ol class="steps">{st}</ol>
</div></section>
<section class="s wrap" id="galeria" aria-labelledby="g-h">
  <h2 id="g-h">Da oficina</h2><p class="lead">Couro bem tratado dura uma vida.</p>
  {gallery(["Sapatos de couro castanho engraxados sobre madeira", "Cinto de couro com fivela metálica", "Mala de couro castanha restaurada", "Sapatos pretos de couro com acabamento brilhante"])}
</section>
<section class="s wrap" id="avaliacoes">
  <h2>Clientes do bairro</h2><p class="lead">Avaliações de exemplo, fictícias. No seu site mostramos as avaliações reais do Google.</p>
  <div class="reviews">{rv}</div>
</section>
<section class="s wrap" id="contacto">
  <h2>Horário &amp; contacto</h2><p class="lead">Passe por cá ou mande uma foto primeiro.</p>
  <div class="visit">
    <ul class="hours"><li><span>Segunda a sexta</span><b>09:00 – 19:00</b></li><li><span>Sábado</span><b>09:30 – 13:00</b></li><li><span>Domingo</span><b>Fechado</b></li></ul>
    <div class="contact"><p><b>Morada</b><br>Rua Imaginária, 00 – Campo de Ourique, Lisboa</p><p><b>WhatsApp</b><br>+351 9XX XXX XXX <small>(fictício)</small></p><a class="pill" href="#contacto">{CHAT_SVG} Enviar foto</a></div>
    <div><div class="map">{map_svg({"bg": "#efe6d6", "block": "#e2d5c0", "park": "#d4dcc0", "road": "#fffaf2", "pin": "#8b4a26", "text": "#6a5847"}, "Mapa ilustrativo de Campo de Ourique com a localização da sapataria", "Rua Ferreira Borges", "Rua Imaginária")}</div>
      <a class="maplink" href="https://www.google.com/maps/search/?api=1&amp;query=Campo+de+Ourique%2C+Lisboa">{PIN_SVG} Abrir no Google Maps</a></div>
  </div>
</section>
</main>
<footer class="f wrap">© Sapataria Meia-Sola – negócio fictício, criado para demonstração.</footer>
<nav class="mcta" aria-label="Ações rápidas"><a href="#contacto">{CHAT_SVG} Enviar foto</a><a class="alt" href="#arranjos">Preços</a></nav>"""
    return doc(lang="pt", title="Sapataria Meia-Sola", desc="Exemplo de site de uma página para um sapateiro em Lisboa (negócio fictício).",
               canon=site + "/demos/sapateiro/", theme="#241a13", font="dmserif", root=root, css=SAPA_CSS, body=body,
               pkg="Vitrine", what="Uma página com tabela de preços, processo em 3 passos, avaliações, horário e botão de contacto fixo no telemóvel.",
               preload_hero="")


# ================================================================== handyman (EN, UK, Vitrine)
HANDY_CSS = """
body{background:#ffffff;color:#14213a;font:17px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
h1,h2,h3,.logo,.big{font-family:"Barlow Condensed","Arial Narrow",system-ui,sans-serif;font-weight:700;font-size-adjust:cap-height from-font;text-transform:uppercase;letter-spacing:.005em}
a{color:#14213a}
.top{background:#14213a;color:#fff}
.nav{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding-block:.9rem}
.logo{font-size:1.6rem;line-height:1;color:#fff;text-decoration:none;display:flex;align-items:center;gap:.55rem}
.logo i{display:inline-grid;place-items:center;width:38px;height:38px;background:#f6c324;color:#14213a;font-style:normal;border-radius:6px;font-size:1.3rem}
.nav ul{display:none;list-style:none;margin:0;padding:0;gap:1.5rem}
.nav ul a{color:#dfe5f0;text-decoration:none;font-weight:500}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;min-block-size:50px;padding:0 1.4rem;border-radius:8px;background:#f6c324;color:#14213a;font-weight:800;text-decoration:none}
.btn.o{background:transparent;color:#fff;border:2px solid #4b5b7c}
.nav .btn{display:none}
.hero{display:grid;gap:2rem;padding-block:1.6rem 3.5rem}
.hero .chip{display:inline-flex;align-items:center;gap:.45rem;background:#22335a;color:#f6c324;font-weight:700;font-size:.85rem;padding:.35rem .8rem;border-radius:999px;margin:0}
.hero h1{font-size:clamp(3rem,11vw,5.8rem);line-height:.92;margin:.8rem 0 1rem;color:#fff}
.hero h1 span{color:#f6c324}
.hero p{color:#c9d2e3;font-size:1.1rem;max-width:40ch;margin:0 0 1.6rem}
.row{display:flex;flex-wrap:wrap;gap:.7rem}
.shot{position:relative;border-radius:12px;overflow:hidden;aspect-ratio:3/2}
.badge{position:absolute;left:.8rem;bottom:.8rem;background:#fff;color:#14213a;border-radius:10px;padding:.6rem .9rem;font-size:.85rem;font-weight:600;box-shadow:0 8px 24px rgba(0,0,0,.25)}
.badge b{display:block;font:700 1.5rem/1 "Barlow Condensed",system-ui,sans-serif}
.trust{background:#f6c324}
.trust ul{list-style:none;margin:0;padding:1rem 0;display:grid;grid-template-columns:1fr 1fr;gap:.6rem 1rem;font-weight:700;font-size:.95rem}
.trust li::before{content:"✓ "}
section.s{padding-block:4rem}
.s h2{font-size:clamp(2.4rem,7vw,3.6rem);line-height:.95;margin-bottom:.6rem}
.s .lead{color:#4b5b7c;max-width:54ch;margin:0 0 2rem}
.grid{display:grid;gap:1rem}
.svc{border:2px solid #e3e8f1;border-radius:12px;padding:1.3rem;display:grid;gap:.3rem;align-content:start}
.svc h3{font-size:1.6rem;line-height:1}
.svc p{margin:0;color:#4b5b7c;font-size:.95rem}
.svc .big{font-size:1.9rem;color:#14213a;margin-top:.4rem}
.svc .big small{font:600 .8rem system-ui,sans-serif;text-transform:none;color:#4b5b7c;margin-right:.25rem}
.note{font-size:.85rem;color:#4b5b7c;margin-top:1rem}
.how{background:#f3f5f9}
.steps{list-style:none;margin:0;padding:0;display:grid;gap:1rem}
.steps li{background:#fff;border-radius:12px;padding:1.3rem;border-left:6px solid #f6c324}
.steps h3{font-size:1.5rem}
.steps p{margin:.2rem 0 0;color:#4b5b7c}
.gal img{border-radius:10px}
.reviews{display:grid;gap:1rem}
.rev{margin:0;background:#14213a;color:#fff;border-radius:12px;padding:1.4rem}
.rev blockquote{margin:.5rem 0 .9rem;font-size:1.05rem}
.rev figcaption{color:#a9b6cf;font-size:.88rem}
.stars{color:#f6c324;letter-spacing:.1em}
.areas{display:flex;flex-wrap:wrap;gap:.5rem;list-style:none;margin:1rem 0 0;padding:0}
.areas li{background:#f3f5f9;border-radius:999px;padding:.35rem .85rem;font-weight:600;font-size:.9rem}
.visit{display:grid;gap:2rem}
.hours{width:100%;border-collapse:collapse}
.hours th,.hours td{text-align:left;padding:.65rem 0;border-bottom:1px solid #e3e8f1;font-weight:500}
.hours td{text-align:right;font-weight:700}
.map{border-radius:12px;overflow:hidden;border:2px solid #e3e8f1}
.maplink{display:inline-flex;align-items:center;gap:.4rem;min-block-size:44px;font-weight:700}
footer.f{padding:2rem 0;border-top:1px solid #e3e8f1;color:#4b5b7c;font-size:.85rem}
.mcta{background:#14213a}
.mcta a{background:#f6c324;color:#14213a;border-radius:8px}
.mcta a.alt{background:transparent;color:#fff;border:2px solid #4b5b7c}
@media(min-width:700px){.grid{grid-template-columns:repeat(2,1fr)}.steps{grid-template-columns:repeat(3,1fr)}.reviews{grid-template-columns:repeat(3,1fr)}.trust ul{grid-template-columns:repeat(4,1fr);text-align:center}}
@media(min-width:900px){
 .nav ul{display:flex}.nav .btn{display:inline-flex}
 .hero{grid-template-columns:1fr 1.05fr;align-items:center;padding-block:3.5rem 4.5rem}
 .grid{grid-template-columns:repeat(3,1fr)}
 .visit{grid-template-columns:1fr 1fr 1.2fr}
}
"""


def handyman(site: str) -> str:
    root = "../../"
    svc = [("Odd jobs & repairs", "Doors that stick, dripping taps, loose handles – the whole list in one visit.", "from", "£45", "/ first hour"),
           ("Flat-pack assembly", "Wardrobes, beds, desks. Packaging taken away.", "from", "£40", ""),
           ("TV & shelf mounting", "Level, secure, cables hidden where possible.", "from", "£55", ""),
           ("Painting & touch-ups", "Single rooms, ceilings, woodwork and doors.", "from", "£180", "/ room"),
           ("Tiling & sealant", "Re-grout and re-seal baths, showers and splashbacks.", "from", "£70", ""),
           ("Fences & gates", "Panels, posts, hinges and latches.", "from", "£90", "")]
    cards = "".join(f'<div class="svc"><h3>{n}</h3><p>{d}</p><span class="big"><small>{f}</small>{p}<small>{u}</small></span></div>' for n, d, f, p, u in svc)
    steps = [("Send a photo", "Text or email a picture of the job and your postcode."), ("Get a fixed price", "A written quote the same working day. No call-out fee."), ("Job done", "We turn up on time, tidy up and send a receipt.")]
    st = "".join(f"<li><h3>{i}. {h}</h3><p>{p}</p></li>" for i, (h, p) in enumerate(steps, 1))
    revs = [("Fixed three doors, a dripping tap and put up blinds in one morning. Fair price, spotless afterwards.", "Claire W., Bishopston"),
            ("Sent a photo at 9am, had a quote by lunch and the fence was fixed on Friday.", "Dev P., Redland"),
            ("Assembled a wardrobe I'd given up on. Polite, quick and took all the cardboard.", "Martin H., Clifton")]
    rv = "".join(f'<figure class="rev">{stars()}<blockquote>“{q}”</blockquote><figcaption>{a} · fictional review</figcaption></figure>' for q, a in revs)
    areas = "".join(f"<li>{a}</li>" for a in ["Clifton", "Redland", "Cotham", "Bishopston", "Southville", "Bedminster", "Easton", "Henleaze"])
    hours = [("Monday – Friday", "08:00 – 18:00"), ("Saturday", "09:00 – 14:00"), ("Sunday", "Closed")]
    hr = "".join(f'<tr><th scope="row">{d}</th><td>{h}</td></tr>' for d, h in hours)
    body = f"""
<div class="top">
<header class="wrap nav">
  <a class="logo" href="#top"><i aria-hidden="true">T</i>Tidy Joist</a>
  <nav aria-label="Sections"><ul><li><a href="#services">Services</a></li><li><a href="#how">How it works</a></li><li><a href="#reviews">Reviews</a></li><li><a href="#contact">Contact</a></li></ul></nav>
  <a class="btn" href="#contact">Get a free quote</a>
</header>
<main id="top">
<section class="wrap hero">
  <div>
    <p class="chip">★ Handyman · Bristol</p>
    <h1>Your to-do list, <span>done properly.</span></h1>
    <p>Small repairs, flat-pack, painting and the jobs nobody else wants. Send a photo, get a fixed price the same day.</p>
    <div class="row"><a class="btn" href="#contact">Get a free quote</a><a class="btn o" href="#services">See prices</a></div>
  </div>
  <div class="shot">{hero_img("handyman", "Drill, spirit level, tape measure and screws on a workbench next to house plans", "(min-width:900px) 50vw, 100vw")}
    <div class="badge"><b>Same day</b>fixed-price quotes</div></div>
</section>
</div>
<div class="trust"><ul class="wrap"><li>Fixed prices</li><li>No call-out fee</li><li>Tidy, on time</li><li>Free quotes</li></ul></div>
<section class="s wrap" id="services">
  <h2>Services &amp; prices</h2><p class="lead">Honest starting prices. You get a fixed quote before any work begins.</p>
  <div class="grid">{cards}</div>
  <p class="note">Example prices – fictional business.</p>
</section>
<section class="s how" id="how"><div class="wrap">
  <h2>How it works</h2><p class="lead">Three steps. No waiting in all day.</p>
  <ol class="steps">{st}</ol>
</div></section>
<section class="s wrap" id="gallery" aria-labelledby="gh">
  <h2 id="gh">Recent work</h2><p class="lead">Every job photographed before and after.</p>
  {gallery(["Hands measuring and marking a part on a workbench", "Wall of neatly organised hand tools in a workshop", "Hammer, gloves and bricks on a wooden floor", "Hand tools laid out on a dark wooden table"])}
</section>
<section class="s wrap" id="reviews">
  <h2>What neighbours say</h2><p class="lead">Example reviews, fictional. On your site we show your real Google reviews.</p>
  <div class="reviews">{rv}</div>
</section>
<section class="s wrap" id="contact">
  <h2>Book a job</h2><p class="lead">Covering North and Central Bristol.</p>
  <div class="visit">
    <div><table class="hours">{hr}</table><ul class="areas" aria-label="Areas covered">{areas}</ul></div>
    <div><p><b>Phone / text</b><br>07XXX XXX XXX <small>(fictional)</small></p><p><b>Email</b><br>hello@tidyjoist.example</p><a class="btn" href="#contact">Send a photo for a quote</a></div>
    <div><div class="map">{map_svg({"bg": "#eef1f6", "block": "#dde3ee", "park": "#d7e7d1", "road": "#ffffff", "pin": "#14213a", "text": "#4b5b7c"}, "Illustrated map of North Bristol showing the service area", "Gloucester Road", "Zetland Road")}</div>
      <a class="maplink" href="https://www.google.com/maps/search/?api=1&amp;query=Bishopston%2C+Bristol">{PIN_SVG} Open in Google Maps</a></div>
  </div>
</section>
</main>
<footer class="f wrap">© Tidy Joist Home Repairs – fictional business, created as a demo.</footer>
<nav class="mcta" aria-label="Quick actions"><a href="#contact">Free quote</a><a class="alt" href="#contact">{PHONE_SVG} Call</a></nav>"""
    return doc(lang="en", title="Tidy Joist – Handyman in Bristol", desc="Example one-page website for a handyman in Bristol, UK (fictional business).",
               canon=site + "/demos/handyman/", theme="#14213a", font="barlow", root=root, css=HANDY_CSS, body=body,
               pkg="Vitrine", what="One long page with prices, a 3-step process, reviews, service area and a sticky call/quote button on mobile.",
               preload_hero="")


# ================================================================== cafe (EN, Ireland, Vitrine)
CAFE_CSS = """
body{background:#f5efe6;color:#2b211c;font:17px/1.65 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
h1,h2,h3,.logo,.pr{font-family:"Young Serif",Georgia,"Times New Roman",serif;font-weight:400;font-size-adjust:from-font}
a{color:#4f6b52}
.nav{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding-block:1.1rem}
.logo{font-size:1.5rem;color:#2b211c;text-decoration:none}
.logo span{color:#a85a3f}
.nav ul{display:none;list-style:none;margin:0;padding:0;gap:1.4rem}
.nav ul a{text-decoration:none;color:#4a3d35}
.btn{display:inline-flex;align-items:center;gap:.5rem;min-block-size:48px;padding:0 1.35rem;border-radius:999px;background:#4f6b52;color:#fff;font-weight:700;text-decoration:none}
.btn.o{background:#fff;color:#2b211c}
.nav .btn{display:none}
.hero{text-align:center;padding-block:1.5rem 3.5rem}
.hero .open{display:inline-flex;align-items:center;gap:.5rem;background:#fff;border-radius:999px;padding:.35rem .9rem;font-size:.88rem;font-weight:600;margin:0}
.hero .open::before{content:"";width:9px;height:9px;border-radius:50%;background:#5c9a61}
.hero h1{font-size:clamp(2.6rem,9vw,5.3rem);line-height:1.02;margin:1rem auto 1rem;max-width:14ch;letter-spacing:-.01em}
.hero h1 span{color:#a85a3f}
.hero p{max-width:44ch;margin:0 auto 1.6rem;color:#5b4c43;font-size:1.1rem}
.row{display:flex;flex-wrap:wrap;gap:.7rem;justify-content:center}
.pic{margin:2.4rem auto 0;max-width:980px;border-radius:28px;overflow:hidden;aspect-ratio:16/10}
section.s{padding-block:4rem}
.s h2{font-size:clamp(2.1rem,6vw,3.2rem);text-align:center;margin-bottom:.4rem}
.s .lead{text-align:center;color:#6c5c52;margin:0 auto 2.2rem;max-width:50ch}
.board{background:#2b211c;color:#f5efe6;border-radius:28px;padding:clamp(1.4rem,5vw,3rem);display:grid;gap:2rem}
.board h3{font-size:1.5rem;color:#e8b49f;margin-bottom:.5rem}
.board ul{list-style:none;margin:0;padding:0}
.board li{display:flex;justify-content:space-between;gap:1rem;padding:.55rem 0;border-bottom:1px solid #46382f}
.board li em{display:block;font-style:normal;font-size:.85rem;color:#bfae9f}
.pr{color:#f5efe6;white-space:nowrap}
.note{text-align:center;font-size:.85rem;color:#6c5c52;margin-top:1rem}
.bake{display:grid;gap:1.5rem;align-items:center;background:#fff;border-radius:28px;padding:1.2rem}
.bake img{border-radius:20px;width:100%;aspect-ratio:4/3;object-fit:cover}
.bake h3{font-size:1.9rem}
.bake p{color:#6c5c52}
.tagx{display:inline-block;background:#f0d9cf;color:#7a3d27;border-radius:999px;padding:.2rem .75rem;font-size:.8rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase}
.gal img{border-radius:18px}
.reviews{display:grid;gap:1rem}
.rev{margin:0;background:#fff;border-radius:22px;padding:1.5rem}
.rev blockquote{margin:.5rem 0 .9rem;font:400 1.15rem/1.45 "Young Serif",Georgia,serif}
.rev figcaption{color:#6c5c52;font-size:.9rem}
.stars{color:#a85a3f;letter-spacing:.1em}
.visit{display:grid;gap:1rem}
.card{background:#fff;border-radius:22px;padding:1.5rem}
.card h3{font-size:1.4rem;margin-bottom:.5rem}
.card p{margin:.25rem 0}
.hours{list-style:none;margin:0;padding:0}
.hours li{display:flex;justify-content:space-between;padding:.45rem 0;border-bottom:1px solid #efe6da}
.map{border-radius:22px;overflow:hidden}
.maplink{display:inline-flex;align-items:center;gap:.4rem;min-block-size:44px;font-weight:700}
footer.f{padding:2rem 0;text-align:center;color:#6c5c52;font-size:.85rem}
.mcta{background:rgba(245,239,230,.95);border-top:1px solid #e6dccd;backdrop-filter:blur(8px)}
.mcta a{background:#4f6b52;color:#fff;border-radius:999px}
.mcta a.alt{background:#fff;color:#2b211c;border:1px solid #d9cdbd}
@media(min-width:700px){.reviews{grid-template-columns:repeat(3,1fr)}.bake{grid-template-columns:1fr 1fr;padding:1.5rem 2.5rem 1.5rem 1.5rem}}
@media(min-width:900px){
 .nav ul{display:flex}.nav .btn{display:inline-flex}
 .board{grid-template-columns:repeat(3,1fr)}
 .visit{grid-template-columns:1fr 1fr 1.3fr}
}
"""


def cafe(site: str) -> str:
    root = "../../"
    menu = [("Coffee", [("Espresso", "", "€2.60"), ("Flat white", "Oat or dairy", "€3.80"), ("Filter of the week", "Irish roaster", "€3.50"), ("Hot chocolate", "", "€3.90")]),
            ("Brunch", [("Sourdough toast", "Butter & jam", "€4.50"), ("Smashed avocado", "Poached egg, chilli", "€11.50"), ("Full Irish (veggie too)", "Until 2pm", "€14.00"), ("Soup & brown bread", "Daily", "€8.50")]),
            ("Bakes", [("Cinnamon bun", "", "€3.60"), ("Scone, cream & jam", "", "€4.20"), ("Banana bread", "", "€3.80"), ("Lemon drizzle", "", "€4.00")])]
    board = "".join("<div><h3>" + c + "</h3><ul>" + "".join(
        f'<li><div>{n}{f"<em>{d}</em>" if d else ""}</div><span class="pr">{p}</span></li>' for n, d, p in items) + "</ul></div>" for c, items in menu)
    revs = [("Best flat white in Stoneybatter and the cinnamon buns sell out by eleven for a reason.", "Aoife M."),
            ("Lovely spot to work for an hour. Staff remember your order after one visit.", "Conor D."),
            ("Brought my parents for brunch – the full Irish was spot on. Dog-friendly too!", "Niamh B.")]
    rv = "".join(f'<figure class="rev">{stars()}<blockquote>“{q}”</blockquote><figcaption>{a} · fictional review</figcaption></figure>' for q, a in revs)
    hours = [("Mon – Fri", "7:30 – 17:00"), ("Saturday", "9:00 – 17:00"), ("Sunday", "9:00 – 15:00")]
    hr = "".join(f"<li><span>{d}</span><b>{h}</b></li>" for d, h in hours)
    body = f"""
<header class="wrap nav">
  <a class="logo" href="#top">Linden <span>&amp;</span> Oat</a>
  <nav aria-label="Sections"><ul><li><a href="#menu">Menu</a></li><li><a href="#bake">Today's bake</a></li><li><a href="#reviews">Reviews</a></li><li><a href="#visit">Visit</a></li></ul></nav>
  <a class="btn" href="#visit">Find us</a>
</header>
<main id="top">
<section class="wrap hero">
  <p class="open">Open today · 7:30 – 17:00</p>
  <h1>Good coffee, <span>slow mornings.</span></h1>
  <p>A neighbourhood café in Stoneybatter, Dublin. Specialty coffee, brunch until 2pm and bakes from our own oven every morning.</p>
  <div class="row"><a class="btn" href="#menu">See the menu</a><a class="btn o" href="#visit">{PIN_SVG} Directions</a></div>
  <div class="pic">{hero_img("cafe", "Bright café interior with hanging lamps, wooden tables and a guest by the window", "(min-width:1000px) 980px, 100vw")}</div>
</section>
<section class="s wrap" id="menu">
  <h2>On the board</h2><p class="lead">Oat milk at no extra charge. Ask about gluten-free bakes.</p>
  <div class="board">{board}</div>
  <p class="note">Example menu and prices – fictional business.</p>
</section>
<section class="s wrap" id="bake">
  <div class="bake"><img src="img/bake.svg" width="600" height="450" alt="Freshly baked chocolate chip cookies piled on a tray" loading="lazy" decoding="async">
    <div><span class="tagx">Today's bake</span><h3>Brown butter &amp; sea salt cookies</h3><p>Out of the oven at 10:00, usually gone by lunch. The owner changes this box from her phone each morning – no developer needed.</p><a class="btn" href="#visit">Come by</a></div></div>
</section>
<section class="s wrap" id="gallery" aria-labelledby="gh">
  <h2 id="gh">Inside the café</h2><p class="lead">Window seats, good light, no rush.</p>
  {gallery(["Flat white with latte art on a saucer with a spoon", "Barista pouring milk into a cappuccino", "Espresso machine pouring a shot into a white cup", "Latte with heart-shaped foam art on a wooden table"])}
</section>
<section class="s wrap" id="reviews">
  <h2>Kind words</h2><p class="lead">Example reviews, fictional. On your site we show your real Google reviews.</p>
  <div class="reviews">{rv}</div>
</section>
<section class="s wrap" id="visit">
  <h2>Come say hello</h2><p class="lead">Walk-ins only. Dogs and laptops welcome (laptops not at weekends).</p>
  <div class="visit">
    <div class="card"><h3>Opening hours</h3><ul class="hours">{hr}</ul></div>
    <div class="card"><h3>Find us</h3><p>00 Imaginary Lane, Stoneybatter, Dublin 7</p><p>Luas Red Line: Museum stop, 4 min walk</p><p>+353 1 XXX XXXX <small>(fictional)</small></p><p>@lindenandoat.demo <small>(fictional)</small></p></div>
    <div><div class="map">{map_svg({"bg": "#ece6da", "block": "#e0d7c7", "park": "#d4e0cc", "road": "#ffffff", "pin": "#4f6b52", "text": "#6c5c52"}, "Illustrated map of Stoneybatter showing the café", "Manor Street", "Imaginary Lane")}</div>
      <a class="maplink" href="https://www.google.com/maps/search/?api=1&amp;query=Stoneybatter%2C+Dublin">{PIN_SVG} Open in Google Maps</a></div>
  </div>
</section>
</main>
<footer class="f wrap">© Linden &amp; Oat – fictional business, created as a demo.</footer>
<nav class="mcta" aria-label="Quick actions"><a href="#visit">{PIN_SVG} Directions</a><a class="alt" href="#menu">Menu</a></nav>"""
    return doc(lang="en", title="Linden & Oat – Café in Dublin", desc="Example one-page website for a neighbourhood café in Dublin (fictional business).",
               canon=site + "/demos/cafe/", theme="#2b211c", font="youngserif", root=root, css=CAFE_CSS, body=body,
               pkg="Vitrine", what="One page with a menu board, a daily special the owner edits, reviews, opening hours and a sticky directions button on mobile.",
               preload_hero="").replace('imagesizes="(min-width:900px) 50vw, 100vw"', 'imagesizes="(min-width:1000px) 980px, 100vw"')


# ================================================================== index
DEMO_LIST = [  # slug, name, niche (pt/en), lang label, package
    ("barbearia", "Barbearia Navalha d'Ouro", "Barbearia · Lisboa", "Barbershop · Lisbon", "PT", "Vitrine"),
    ("tasca", "Tasca do Pátio Azul", "Tasca / restaurante · Lisboa", "Tavern / restaurant · Lisbon", "PT + EN", "Maison"),
    ("sapateiro", "Sapataria Meia-Sola", "Sapateiro & chaves · Lisboa", "Shoe repair & keys · Lisbon", "PT", "Vitrine"),
    ("cafe", "Linden & Oat", "Café · Dublin", "Café · Dublin", "EN", "Vitrine"),
    ("handyman", "Tidy Joist", "Faz-tudo · Bristol", "Handyman / trades · Bristol", "EN", "Vitrine"),
]


def index(site: str) -> str:
    cards = "".join(f"""
    <a class="d" href="./{slug}/">
      <img src="./{slug}/img/hero-560.svg" width="{IMG[slug]['hero_s'][0]}" height="{IMG[slug]['hero_s'][1]}" alt="" loading="{'eager' if i < 2 else 'lazy'}" decoding="async">
      <div class="t"><span class="pill">{lang} · {pkg} · {PKG[pkg][1]['pt']}</span><h2>{_e(name)}</h2><p>{niche_pt}<br><span lang="en">{niche_en}</span></p><span class="go">Ver demo / Open demo →</span></div></a>"""
        for i, (slug, name, niche_pt, niche_en, lang, pkg) in enumerate(DEMO_LIST))
    return f"""<!DOCTYPE html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index, follow">
  <title>Demos de sites para pequenos negócios — Desire Agency</title>
  <meta name="description" content="Cinco exemplos de sites para negócios fictícios: barbearia, tasca, sapateiro (Lisboa), café (Dublin) e faz-tudo (Bristol). Pacote Vitrine a partir de 390 €.">
  <link rel="canonical" href="{site}/demos/">
  <meta name="theme-color" content="#06060c">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <style>
  *{{box-sizing:border-box}}body{{margin:0;background:#06060c;color:#f4f4f7;font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}}
  img{{display:block;max-width:100%;height:auto}}h1,h2{{text-wrap:balance}}
  .w{{max-width:1140px;margin:0 auto;padding:2.5rem clamp(1.1rem,4vw,2rem)}}a{{color:#ff9cf0}}
  .top{{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;font-size:.95rem}}
  .top a{{min-height:44px;display:inline-flex;align-items:center}}
  .brand{{font-weight:700;letter-spacing:.16em;text-transform:uppercase;background:linear-gradient(90deg,#ff5ee6,#b45cff,#3fe6f2);-webkit-background-clip:text;background-clip:text;color:transparent;text-decoration:none}}
  h1{{font-size:clamp(2rem,5vw,3.2rem);line-height:1.1;margin:2rem 0 .6rem}}
  .lede{{color:#c4bfdc;max-width:64ch}}
  .g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1.2rem;margin-top:2rem}}
  .d{{display:flex;flex-direction:column;border:1px solid rgba(255,255,255,.12);border-radius:18px;overflow:hidden;text-decoration:none;color:inherit;background:#0e0e1c;transition:transform .2s,border-color .2s}}
  .d:hover,.d:focus-visible{{transform:translateY(-3px);border-color:#ff5ee6}}
  .d img{{width:100%;aspect-ratio:16/10;object-fit:cover}}
  .t{{padding:1rem 1.15rem 1.3rem}}.t h2{{margin:.55rem 0 .2rem;font-size:1.3rem}}.t p{{margin:0 0 .6rem;color:#c4bfdc;font-size:.95rem}}
  .pill{{font-size:.75rem;font-weight:700;color:#3fe6f2;border:1px solid rgba(63,230,242,.4);border-radius:999px;padding:.15rem .6rem}}
  .go{{color:#ff9cf0;font-weight:600}}.note{{color:#a29cbf;font-size:.88rem;margin-top:2rem}}
  .cta{{display:inline-flex;align-items:center;min-height:48px;margin-top:1.8rem;padding:0 1.4rem;border-radius:999px;background:linear-gradient(90deg,#ff5ee6,#b45cff,#3fe6f2);color:#14041a;font-weight:700;text-decoration:none}}
  @media (prefers-reduced-motion:reduce){{.d{{transition:none}}}}
  </style>
</head>
<body><main class="w">
  <div class="top"><a class="brand" href="../">Desire Agency</a><span><a href="../pt/websites/">PT</a> · <a href="../websites/">EN</a> · <a href="../de/websites/">DE</a></span></div>
  <h1>Demos: sites para pequenos negócios</h1>
  <p class="lede">Cinco exemplos, cada um com o seu próprio estilo. Os negócios são fictícios: nomes, moradas, contactos, preços, horários e avaliações são inventados. Mostram como pode ficar o seu site no telemóvel – pacote <strong>Vitrine</strong> a partir de 390 €, bilingue com <strong>Maison</strong> a partir de 1190 €.<br><span lang="en">Five example sites for fictional businesses in Lisbon, Dublin and Bristol.</span> · <span lang="de">Fünf Beispielseiten für fiktive Betriebe in Lissabon, Dublin und Bristol.</span></p>
  <div class="g">{cards}
  </div>
  <a class="cta" href="../pt/websites/#contacto">Pedir orçamento sem compromisso →</a>
  <p class="note">{VAT["pt"]} Pagamento só após conclusão. Fotografias CC0 (StockSnap.io) e tipos de letra SIL OFL – <a href="credits.txt">créditos</a>.</p>
</main></body>
</html>
"""


def pages(site: str) -> dict:
    return {
        "demos/index.html": index(site),
        "demos/barbearia/index.html": barbearia(site),
        "demos/tasca/index.html": tasca(site, "pt"),
        "demos/tasca/en/index.html": tasca(site, "en"),
        "demos/sapateiro/index.html": sapateiro(site),
        "demos/cafe/index.html": cafe(site),
        "demos/handyman/index.html": handyman(site),
    }
