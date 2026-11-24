"""Demo one-pagers for fictional Lisbon businesses (PT-PT). Imported by build.py.

All businesses, names, addresses, prices and hours are invented. Graphics are inline SVG/CSS
drawn for this site (no stock photos, no third-party logos, no external requests).
"""
from __future__ import annotations

BANNER_CSS = """
.demo-bar{position:sticky;top:0;z-index:50;background:#06060c;color:#f4f4f7;font:600 13px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;padding:.55rem 1rem;display:flex;flex-wrap:wrap;gap:.4rem 1rem;align-items:center;justify-content:center;text-align:center;border-bottom:2px solid #ff5ee6}
.demo-bar b{color:#3fe6f2;letter-spacing:.04em;text-transform:uppercase}
.demo-bar a{color:#ff9cf0}
.demo-cta{background:#06060c;color:#f4f4f7;text-align:center;padding:2.5rem 1.2rem;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
.demo-cta h2{margin:0 0 .5rem;font-size:1.35rem}
.demo-cta p{margin:.3rem auto;max-width:620px;color:#c9c4e0;font-size:.95rem}
.demo-cta a.go{display:inline-block;margin-top:1rem;padding:.8rem 1.3rem;border-radius:999px;background:linear-gradient(90deg,#ff5ee6,#b45cff,#3fe6f2);color:#14041a;font-weight:700;text-decoration:none}
.demo-cta small{display:block;margin-top:1rem;color:#8f89ab}
"""


def _bar(label_extra: str = "") -> str:
    return ('<div class="demo-bar" role="note"><b>Exemplo / demo – negócio fictício</b>'
            '<span>Nome, morada, contactos, preços e horários são inventados. '
            'Site de demonstração da <a href="../../pt/websites/">Desire Agency</a>.</span></div>')


def _cta() -> str:
    return """
<section class="demo-cta" aria-label="Desire Agency">
  <h2>Quer um site assim para o seu negócio?</h2>
  <p>Este exemplo corresponde ao pacote <strong>Vitrine</strong>: uma página, pensada para o telemóvel, a partir de 390 €.</p>
  <p>Preços finais. IVA isento ao abrigo do artigo 53.º do CIVA. Pagamento só após conclusão.</p>
  <a class="go" href="../../pt/websites/#contacto">Pedir orçamento sem compromisso →</a>
  <small>Exemplo / demo – negócio fictício · Ilustrações em SVG/CSS próprias, sem fotografias de banco de imagens · <a href="../" style="color:#ff9cf0">Ver todas as demos</a></small>
</section>"""


def _doc(title: str, desc: str, css: str, body: str, canon: str, theme: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-PT">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, follow">
  <title>{title} (demo – negócio fictício)</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{canon}">
  <meta name="theme-color" content="{theme}">
  <link rel="icon" href="../../favicon.svg" type="image/svg+xml">
  <style>{BANNER_CSS}{css}</style>
</head>
<body>
{_bar()}
{body}
{_cta()}
</body>
</html>
"""


# ---------------------------------------------------------------- barbearia
BARBER_CSS = """
*{box-sizing:border-box}body{margin:0;background:#111;color:#eee;font:16px/1.6 Georgia,"Times New Roman",serif}
a{color:#e0b45c}.w{max-width:1000px;margin:0 auto;padding:0 1.2rem}
header.h{background:radial-gradient(circle at 80% 20%,#3a2a10 0,#111 60%);padding:3.5rem 0 3rem}
.h .w{display:grid;grid-template-columns:1.3fr 1fr;gap:2rem;align-items:center}
.h small{letter-spacing:.3em;text-transform:uppercase;color:#e0b45c;font:700 .75rem/1 system-ui,sans-serif}
.h h1{font-size:clamp(2.2rem,6vw,3.6rem);line-height:1.05;margin:.6rem 0}
.h p{color:#cfc6b4;max-width:34ch}
.btn{display:inline-block;padding:.85rem 1.3rem;border-radius:4px;background:#e0b45c;color:#111;font:700 1rem system-ui,sans-serif;text-decoration:none;margin:.3rem .5rem .3rem 0}
.btn.o{background:transparent;color:#e0b45c;border:1px solid #e0b45c}
section{padding:3rem 0;border-top:1px solid #2a2a2a}
h2{font-size:1.8rem;margin:0 0 1.2rem;color:#e0b45c}
.price{display:grid;grid-template-columns:1fr auto;gap:.2rem 1rem;max-width:560px}
.price div{border-bottom:1px dotted #555;padding:.55rem 0}.price span{font-family:system-ui,sans-serif;color:#aaa;font-size:.85rem;display:block}
.price b{padding:.55rem 0;border-bottom:1px dotted #555;text-align:right}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:2rem}
table{border-collapse:collapse;width:100%;font-family:system-ui,sans-serif}td{padding:.45rem 0;border-bottom:1px solid #2a2a2a}td+td{text-align:right}
.map{height:200px;border-radius:6px;background:repeating-linear-gradient(45deg,#1c1c1c 0 14px,#222 14px 28px);display:grid;place-items:center;color:#888;font-family:system-ui,sans-serif;font-size:.9rem}
.rev{background:#1a1a1a;border-left:3px solid #e0b45c;padding:1rem;font-style:italic;color:#bbb}
.fab{position:fixed;right:1rem;bottom:1rem;z-index:40;border-radius:999px;box-shadow:0 6px 20px rgba(0,0,0,.5)}
@media(max-width:720px){.h .w,.cols{grid-template-columns:1fr}.h svg{max-width:220px;margin:0 auto;display:block}}
"""
BARBER_SVG = """<svg viewBox="0 0 200 240" role="img" aria-label="Ilustração: poste de barbeiro e tesoura">
<rect x="70" y="10" width="60" height="16" rx="8" fill="#e0b45c"/><rect x="70" y="214" width="60" height="16" rx="8" fill="#e0b45c"/>
<clipPath id="c"><rect x="78" y="26" width="44" height="188" rx="22"/></clipPath>
<g clip-path="url(#c)"><rect x="78" y="26" width="44" height="188" fill="#f4f1ea"/>
<g fill="#b3261e">""" + "".join(f'<path d="M78 {y} l44 -30 v14 l-44 30z"/>' for y in range(40, 260, 34)) + """</g>
<g fill="#1f3c88">""" + "".join(f'<path d="M78 {y} l44 -30 v7 l-44 30z"/>' for y in range(57, 260, 34)) + """</g></g>
<g transform="translate(150 150) rotate(-30)" fill="none" stroke="#e0b45c" stroke-width="5"><circle cx="-10" cy="40" r="12"/><circle cx="14" cy="40" r="12"/><path d="M-4 30 L10 -40 M8 30 L-6 -40"/></g>
</svg>"""


def barbearia(site: str) -> str:
    body = f"""
<header class="h"><div class="w">
  <div>
    <small>Arroios · Lisboa · desde 2012 (fictício)</small>
    <h1>Barbearia Navalha d'Ouro</h1>
    <p>Cortes clássicos, barba à navalha com toalha quente e conversa boa. Marque em 30 segundos pelo WhatsApp.</p>
    <a class="btn" href="#marcar">Marcar pelo WhatsApp</a><a class="btn o" href="#precos">Ver preços</a>
  </div>
  {BARBER_SVG}
</div></header>
<main class="w">
<section id="precos"><h2>Serviços e preços</h2>
  <div class="price">
    <div>Corte clássico<span>tesoura e máquina, 30 min</span></div><b>14 €</b>
    <div>Barba à navalha<span>toalha quente, 25 min</span></div><b>12 €</b>
    <div>Corte + barba<span>45 min</span></div><b>23 €</b>
    <div>Corte criança<span>até aos 12 anos</span></div><b>10 €</b>
    <div>Pigmentação de barba<span>20 min</span></div><b>8 €</b>
  </div>
  <p style="font-family:system-ui,sans-serif;font-size:.85rem;color:#999">Preços de exemplo.</p>
</section>
<section class="cols" id="marcar">
  <div><h2>Horário</h2><table>
    <tr><td>Segunda</td><td>Fechado</td></tr><tr><td>Terça a sexta</td><td>10:00 – 20:00</td></tr>
    <tr><td>Sábado</td><td>09:00 – 18:00</td></tr><tr><td>Domingo</td><td>Fechado</td></tr></table></div>
  <div><h2>Marcações</h2>
    <p>Envie mensagem com o dia e a hora que prefere – respondemos no próprio dia.</p>
    <a class="btn" href="#marcar" title="Demo: botão sem ligação">WhatsApp +351 9XX XXX XXX</a>
    <p style="font-family:system-ui,sans-serif;font-size:.85rem;color:#999">Demo: número e botão fictícios.</p></div>
</section>
<section class="cols">
  <div><h2>Onde estamos</h2><p>Rua Inventada, 00 – Arroios, Lisboa<br>Metro Arroios (linha verde), 3 min a pé</p>
    <div class="map" role="img" aria-label="Espaço para o mapa">Aqui entra o mapa do Google</div></div>
  <div><h2>O que dizem os clientes</h2>
    <p class="rev">Aqui aparecem as suas avaliações reais do Google, com ligação para o perfil.</p>
    <p style="font-family:system-ui,sans-serif;font-size:.85rem;color:#999">Nesta demo não mostramos avaliações inventadas.</p></div>
</section>
</main>
<a class="btn fab" href="#marcar" aria-label="Marcar pelo WhatsApp (demo)">WhatsApp</a>"""
    return _doc("Barbearia Navalha d'Ouro", "Exemplo de site de uma página para uma barbearia em Lisboa (negócio fictício).",
                BARBER_CSS, body, site + "/demos/barbearia/", "#111111")


# ---------------------------------------------------------------- tasca
TASCA_CSS = """
*{box-sizing:border-box}body{margin:0;background:#fbf8f1;color:#1d2433;font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
.w{max-width:980px;margin:0 auto;padding:0 1.2rem}
.azul{background-color:#1f4e9c;background-image:radial-gradient(circle at 50% 50%,transparent 9px,#fbf8f1 10px,#fbf8f1 12px,transparent 13px),linear-gradient(45deg,transparent 45%,rgba(255,255,255,.35) 46% 54%,transparent 55%),linear-gradient(-45deg,transparent 45%,rgba(255,255,255,.35) 46% 54%,transparent 55%);background-size:48px 48px}
header.h{padding:3rem 0}
.card{background:#fbf8f1;border-radius:10px;padding:2rem;max-width:620px;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.card small{color:#1f4e9c;font-weight:700;letter-spacing:.2em;text-transform:uppercase;font-size:.75rem}
h1{font-family:Georgia,serif;font-size:clamp(2.1rem,6vw,3.3rem);line-height:1.05;margin:.5rem 0;color:#1f4e9c}
.btn{display:inline-block;padding:.8rem 1.2rem;border-radius:8px;background:#c8442d;color:#fff;font-weight:700;text-decoration:none;margin:.3rem .4rem .3rem 0}
.btn.o{background:#fff;color:#1f4e9c;border:2px solid #1f4e9c}
section{padding:2.6rem 0}h2{font-family:Georgia,serif;color:#1f4e9c;font-size:1.8rem;margin:0 0 1rem}
.dia{background:#fff;border:2px dashed #c8442d;border-radius:10px;padding:1.2rem 1.4rem;display:flex;flex-wrap:wrap;justify-content:space-between;gap:.5rem;align-items:center}
.dia b{font-size:1.2rem}.dia span{color:#c8442d;font-weight:800;font-size:1.3rem}
.menu{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem}
.menu h3{margin:.2rem 0 .6rem;font-size:1rem;text-transform:uppercase;letter-spacing:.12em;color:#c8442d}
.menu li{display:flex;justify-content:space-between;gap:1rem;padding:.4rem 0;border-bottom:1px solid #e6dfd0}.menu ul{list-style:none;margin:0;padding:0}
.info{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}.info div{background:#fff;border-radius:10px;padding:1.1rem;border-top:4px solid #1f4e9c}
.lang{float:right;font-size:.85rem;background:#fff;border-radius:999px;padding:.2rem .7rem;color:#1f4e9c;font-weight:700}
@media(max-width:720px){.menu,.info{grid-template-columns:1fr}}
"""


def tasca(site: str) -> str:
    body = """
<header class="h azul"><div class="w"><div class="card">
  <span class="lang" title="No pacote Maison: PT/EN">PT · EN</span>
  <small>Graça · Lisboa (fictício)</small>
  <h1>Tasca do Pátio Azul</h1>
  <p>Comida portuguesa de sempre, feita todos os dias. Prato do dia ao almoço, petiscos ao jantar e vinho da casa a copo.</p>
  <a class="btn" href="#reservar">Ligar para reservar</a><a class="btn o" href="#ementa">Ver ementa</a>
</div></div></header>
<main class="w">
<section><h2>Prato do dia</h2>
  <div class="dia"><div><b>Terça: Bacalhau à Brás</b><br>com salada e pão · bebida e café incluídos</div><span>11,50 €</span></div>
  <p style="font-size:.85rem;color:#6b6457">Atualizado todas as manhãs – o dono muda o texto em 1 minuto, sem programador.</p>
</section>
<section id="ementa"><h2>Ementa</h2><div class="menu">
  <div><h3>Petiscos</h3><ul><li>Pica-pau do lombo<b>8,50 €</b></li><li>Peixinhos da horta<b>5,00 €</b></li><li>Queijo de Azeitão com tostas<b>7,50 €</b></li><li>Caldo verde<b>3,00 €</b></li></ul></div>
  <div><h3>Pratos</h3><ul><li>Bitoque com ovo<b>10,50 €</b></li><li>Polvo à lagareiro<b>17,00 €</b></li><li>Arroz de pato<b>12,00 €</b></li><li>Sardinhas assadas (época)<b>12,50 €</b></li></ul></div>
  <div><h3>Sobremesas</h3><ul><li>Arroz doce<b>3,50 €</b></li><li>Baba de camelo<b>3,50 €</b></li></ul></div>
  <div><h3>Bebidas</h3><ul><li>Vinho da casa (copo)<b>2,50 €</b></li><li>Imperial<b>1,80 €</b></li></ul></div>
</div><p style="font-size:.85rem;color:#6b6457">Pratos e preços de exemplo.</p></section>
<section id="reservar"><h2>Horário e reservas</h2><div class="info">
  <div><b>Almoço</b><br>Terça a sábado<br>12:00 – 15:00</div>
  <div><b>Jantar</b><br>Quinta a sábado<br>19:30 – 23:00</div>
  <div><b>Reservas</b><br>Telefone +351 21X XXX XXX<br><small>(demo: número fictício)</small></div>
</div>
<p style="margin-top:1rem">Largo Inventado, 00 – Graça, Lisboa · Elétrico 28, paragem a 2 minutos.</p></section>
</main>"""
    return _doc("Tasca do Pátio Azul", "Exemplo de site de uma página para uma tasca em Lisboa (negócio fictício).",
                TASCA_CSS, body, site + "/demos/tasca/", "#1f4e9c")


# ---------------------------------------------------------------- sapateiro
SAPA_CSS = """
*{box-sizing:border-box}body{margin:0;background:#f6efe6;color:#2b1d14;font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
.w{max-width:980px;margin:0 auto;padding:0 1.2rem}
header.h{background:#5a3522;color:#f6efe6;padding:3rem 0;background-image:repeating-linear-gradient(90deg,rgba(255,255,255,.03) 0 2px,transparent 2px 9px)}
.h .w{display:grid;grid-template-columns:1.3fr 1fr;gap:2rem;align-items:center}
.h small{color:#f0b46a;font-weight:700;letter-spacing:.2em;text-transform:uppercase;font-size:.75rem}
h1{font-family:Georgia,serif;font-size:clamp(2.1rem,6vw,3.3rem);line-height:1.05;margin:.5rem 0}
.btn{display:inline-block;padding:.8rem 1.2rem;border-radius:999px;background:#f0b46a;color:#2b1d14;font-weight:800;text-decoration:none;margin:.3rem .4rem .3rem 0}
.btn.o{background:transparent;color:#f6efe6;border:2px solid #f0b46a}
section{padding:2.6rem 0}h2{font-family:Georgia,serif;color:#5a3522;font-size:1.8rem;margin:0 0 1rem}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}
.it{background:#fff;border-radius:14px;padding:1.1rem;box-shadow:0 2px 0 #e3d5c3}
.it b{display:block;font-size:1.05rem}.it span{color:#8a5a3c;font-weight:800;font-size:1.2rem}
.steps{counter-reset:s;display:grid;grid-template-columns:repeat(3,1fr);gap:1rem}
.steps div{background:#fff;border-radius:14px;padding:1.1rem 1.1rem 1.1rem 3.4rem;position:relative}
.steps div::before{counter-increment:s;content:counter(s);position:absolute;left:1rem;top:1rem;width:1.8rem;height:1.8rem;border-radius:50%;background:#5a3522;color:#f6efe6;display:grid;place-items:center;font-weight:800}
.hours{background:#fff;border-radius:14px;padding:1.2rem;max-width:520px}
.hours p{display:flex;justify-content:space-between;margin:.3rem 0;border-bottom:1px dashed #e3d5c3}
@media(max-width:760px){.h .w,.grid,.steps{grid-template-columns:1fr}.h svg{max-width:240px;margin:0 auto;display:block}}
"""
SAPA_SVG = """<svg viewBox="0 0 240 160" role="img" aria-label="Ilustração: sapato e martelo de sapateiro">
<path d="M20 110 C20 80 40 70 70 72 L110 74 C130 76 140 60 150 50 L175 52 C178 80 200 92 222 98 C232 101 232 122 222 124 L30 124 C22 124 20 118 20 110Z" fill="#f0b46a"/>
<path d="M20 124 L222 124 L222 132 L20 132Z" fill="#2b1d14"/>
<path d="M150 50 C160 70 168 82 190 90" fill="none" stroke="#5a3522" stroke-width="3" stroke-dasharray="5 5"/>
<g transform="translate(70 20) rotate(25)"><rect x="0" y="0" width="12" height="70" rx="5" fill="#d9c3a5"/><rect x="-14" y="-10" width="40" height="16" rx="4" fill="#cfd6dd"/></g>
</svg>"""


def sapateiro(site: str) -> str:
    body = f"""
<header class="h"><div class="w">
  <div>
    <small>Campo de Ourique · Lisboa (fictício)</small>
    <h1>Sapataria Meia-Sola</h1>
    <p>Arranjos de calçado, malas e cintos feitos à mão. A maioria fica pronta em 48 horas.</p>
    <a class="btn" href="#contacto-demo">Pedir orçamento por foto</a><a class="btn o" href="#arranjos">Ver preços</a>
  </div>
  {SAPA_SVG}
</div></header>
<main class="w">
<section id="arranjos"><h2>Arranjos e preços</h2><div class="grid">
  <div class="it"><b>Meias-solas</b>sola de couro ou borracha<br><span>desde 18 €</span></div>
  <div class="it"><b>Tacões</b>senhora ou homem<br><span>desde 8 €</span></div>
  <div class="it"><b>Fechos de botas</b>substituição completa<br><span>desde 15 €</span></div>
  <div class="it"><b>Costuras</b>sapatos, malas, cintos<br><span>desde 6 €</span></div>
  <div class="it"><b>Alargar calçado</b>com forma, 24 h<br><span>7 €</span></div>
  <div class="it"><b>Limpeza e graxa</b>couro e camurça<br><span>desde 5 €</span></div>
</div><p style="font-size:.85rem;color:#8a5a3c">Preços de exemplo. O preço final é confirmado ao ver a peça.</p></section>
<section><h2>Como funciona</h2><div class="steps">
  <div><b>Envie uma foto</b><br>pelo WhatsApp, com o que precisa de arranjar.</div>
  <div><b>Receba o preço</b><br>respondemos no mesmo dia útil.</div>
  <div><b>Deixe e levante</b><br>a maioria dos arranjos fica pronta em 48 h.</div>
</div></section>
<section id="contacto-demo"><h2>Horário e contacto</h2><div class="hours">
  <p><span>Segunda a sexta</span><b>09:00 – 19:00</b></p><p><span>Sábado</span><b>09:30 – 13:00</b></p><p><span>Domingo</span><b>Fechado</b></p>
  <p style="border:0;display:block;margin-top:.8rem">Rua Imaginária, 00 – Campo de Ourique, Lisboa<br>WhatsApp +351 9XX XXX XXX <small>(demo: número fictício)</small></p>
</div></section>
</main>"""
    return _doc("Sapataria Meia-Sola", "Exemplo de site de uma página para um sapateiro em Lisboa (negócio fictício).",
                SAPA_CSS, body, site + "/demos/sapateiro/", "#5a3522")


# ---------------------------------------------------------------- index
def index(site: str) -> str:
    items = [("barbearia", "Barbearia Navalha d'Ouro", "Barbearia", "#111", "#e0b45c"),
             ("tasca", "Tasca do Pátio Azul", "Restaurante / tasca", "#1f4e9c", "#fbf8f1"),
             ("sapateiro", "Sapataria Meia-Sola", "Sapateiro / oficina", "#5a3522", "#f0b46a")]
    cards = "".join(f"""
    <a class="d" href="./{slug}/"><div class="sw" style="background:{bg};color:{fg}">{niche}</div>
      <div class="t"><span class="pill">Exemplo / demo – negócio fictício</span><h2>{name}</h2><span class="go">Ver demo →</span></div></a>""" for slug, name, niche, bg, fg in items)
    return f"""<!DOCTYPE html>
<html lang="pt-PT" data-theme="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="index, follow">
  <title>Demos de sites para pequenos negócios — Desire Agency</title>
  <meta name="description" content="Três exemplos de sites de uma página para negócios fictícios de Lisboa: barbearia, tasca e sapateiro. Pacote Vitrine a partir de 390 €.">
  <link rel="canonical" href="{site}/demos/">
  <meta name="theme-color" content="#06060c">
  <link rel="icon" href="../favicon.svg" type="image/svg+xml">
  <style>
  *{{box-sizing:border-box}}body{{margin:0;background:#06060c;color:#f4f4f7;font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}}
  .w{{max-width:1040px;margin:0 auto;padding:2.5rem 1.2rem}}a{{color:#ff9cf0}}
  .top{{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;font-size:.9rem}}
  .brand{{font-weight:700;letter-spacing:.16em;text-transform:uppercase;background:linear-gradient(90deg,#ff5ee6,#b45cff,#3fe6f2);-webkit-background-clip:text;background-clip:text;color:transparent;text-decoration:none}}
  h1{{font-size:clamp(2rem,5vw,3rem);line-height:1.1;margin:2rem 0 .6rem;text-shadow:0 0 24px rgba(255,94,230,.35)}}
  .lede{{color:#b0abc9;max-width:60ch}}
  .g{{display:grid;grid-template-columns:repeat(3,1fr);gap:1.1rem;margin-top:2rem}}
  .d{{display:block;border:1px solid rgba(255,255,255,.12);border-radius:16px;overflow:hidden;text-decoration:none;color:inherit;background:#0e0e1c;transition:transform .2s,border-color .2s}}
  .d:hover{{transform:translateY(-3px);border-color:#ff5ee6}}
  .sw{{height:120px;display:grid;place-items:center;font:700 1.1rem Georgia,serif}}
  .t{{padding:1rem 1.1rem 1.2rem}}.t h2{{margin:.5rem 0;font-size:1.2rem}}
  .pill{{font-size:.72rem;font-weight:700;color:#3fe6f2;border:1px solid rgba(63,230,242,.4);border-radius:999px;padding:.15rem .55rem}}
  .go{{color:#ff9cf0;font-weight:600}}.note{{color:#8f89ab;font-size:.85rem;margin-top:2rem}}
  .cta{{display:inline-block;margin-top:1.5rem;padding:.8rem 1.3rem;border-radius:999px;background:linear-gradient(90deg,#ff5ee6,#b45cff,#3fe6f2);color:#14041a;font-weight:700;text-decoration:none}}
  @media(max-width:760px){{.g{{grid-template-columns:1fr}}}}
  </style>
</head>
<body><main class="w">
  <div class="top"><a class="brand" href="../">Desire Agency</a><span><a href="../pt/websites/">PT</a> · <a href="../websites/">EN</a> · <a href="../de/websites/">DE</a></span></div>
  <h1>Demos: sites de uma página</h1>
  <p class="lede">Três exemplos para negócios típicos de Lisboa. Os negócios são fictícios: nomes, moradas, contactos, preços e horários são inventados. Mostram como pode ficar um site <strong>Vitrine</strong> (a partir de 390 €) no telemóvel.<br><span lang="en">Three example sites for fictional Lisbon businesses.</span> · <span lang="de">Drei Beispielseiten für fiktive Lissabonner Betriebe.</span></p>
  <div class="g">{cards}
  </div>
  <a class="cta" href="../pt/websites/#contacto">Pedir orçamento sem compromisso →</a>
  <p class="note">Preços finais. IVA isento ao abrigo do artigo 53.º do CIVA. Pagamento só após conclusão. Ilustrações em SVG/CSS feitas para este site; sem fotografias de banco de imagens nem logótipos de terceiros.</p>
</main></body>
</html>
"""


def pages(site: str) -> dict:
    return {
        "demos/index.html": index(site),
        "demos/barbearia/index.html": barbearia(site),
        "demos/tasca/index.html": tasca(site),
        "demos/sapateiro/index.html": sapateiro(site),
    }
