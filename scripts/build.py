#!/usr/bin/env python3
"""Genereert de statische pagina's in public/ vanuit content/.

Gebruik:  python3 scripts/build.py
Nieuwe post: voeg een item toe aan content/posts.json en maak
content/posts/<slug>.html met de tekst (<p>, <h3>, <strong>, <em>).
"""
import json
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
SITE = "https://vanwezelbos.nl"
NAME = "Het Van Wezelbos"
DESC = ("Het Van Wezelbos is een familiebos dat stap voor stap wordt omgevormd tot een "
        "gezond, klimaatbestendig loofbos vol leven. Volg het beheerplan 2024–2050.")
PDF = "/documenten/bosbeheerplan-van-wezel-bos.pdf"

posts = sorted(json.loads((ROOT / "content/posts.json").read_text()),
               key=lambda p: p["date"], reverse=True)
e = html.escape


def layout(title, body, *, path, desc=DESC, image="/img/toekomstbomen-1.jpg", home=False, og="website"):
    full_title = NAME if home else f"{title} — {NAME}"
    return f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta property="og:type" content="{og}">
<meta property="og:locale" content="nl_NL">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE}{image}">
<meta property="og:url" content="{SITE}{path}">
<meta name="theme-color" content="#1c3326">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/style.css">
</head>
<body class="{'home' if home else ''}">
<a class="skip" href="#main">Naar de inhoud</a>
<header class="site-header" id="top">
  <div class="wrap bar">
    <a class="brand" href="/" aria-label="{NAME} — home">
      <svg viewBox="0 0 32 32" width="26" height="26" aria-hidden="true"><path d="M16 2 6 15h5l-4 7h6v6h6v-6h6l-4-7h5z" fill="currentColor"/></svg>
      <span>Van Wezelbos</span>
    </a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav"><span class="sr">Menu</span><i></i><i></i></button>
    <nav id="nav" class="nav">
      <a href="/#over-het-bos">Over het bos</a>
      <a href="/blog/">Nieuws</a>
      <a href="{PDF}" class="pill" target="_blank" rel="noopener">Beheerplan</a>
    </nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap foot">
    <div>
      <p class="foot-title">{NAME}</p>
      <p class="muted">Een familiebos in transitie — naar een gezond, klimaatbestendig loofbos.</p>
    </div>
    <ul>
      <li><a href="/">Home</a></li>
      <li><a href="/blog/">Nieuws</a></li>
      <li><a href="{PDF}" target="_blank" rel="noopener">Bosbeheerplan 2024–2050 (PDF)</a></li>
    </ul>
  </div>
  <div class="wrap legal">© 2026 vanwezelbos.nl</div>
</footer>
<script src="/js/site.js" defer></script>
</body>
</html>
"""


def card(p):
    return f"""<a class="card reveal" href="/blog/{p['slug']}/">
  <div class="card-img"><img src="/img/{p['hero']}" alt="{e(p['heroAlt'])}" loading="lazy"></div>
  <div class="card-body">
    <span class="tag">Werkzaamheden · {e(p['label'])}</span>
    <h3>{e(p['title'])}</h3>
    <p>{e(p['excerpt'])}</p>
    <span class="more">Lees verder <b aria-hidden="true">→</b></span>
  </div>
</a>"""


def home():
    cards = "\n".join(card(p) for p in posts[:3])
    body = f"""
<section class="hero">
  <img src="/img/toekomstbomen-1.jpg" alt="Rododendrons en dennen in het Van Wezelbos" fetchpriority="high">
  <div class="hero-shade"></div>
  <div class="wrap hero-in">
    <p class="eyebrow">Beheerplan 2024–2050</p>
    <h1>Het Van Wezelbos</h1>
    <p class="lede">Een dennenbos met een eeuw aan familiegeschiedenis, dat stap voor stap groeit naar een gezond, klimaatbestendig loofbos vol leven.</p>
    <div class="cta">
      <a class="btn" href="/blog/">Volg de werkzaamheden</a>
      <a class="btn ghost" href="#over-het-bos">Over het bos</a>
    </div>
  </div>
  <a class="scroll" href="#stats" aria-label="Scroll naar beneden"><span></span></a>
</section>

<section class="stats" id="stats">
  <div class="wrap grid4">
    <div class="reveal"><b>±100</b><span>jaar in de familie</span></div>
    <div class="reveal"><b>200+</b><span>nieuwe boompjes geplant</span></div>
    <div class="reveal"><b>5</b><span>soorten: esdoorn, beuk, eik, hazelaar &amp; wilde kers</span></div>
    <div class="reveal"><b>2050</b><span>horizon van het beheerplan</span></div>
  </div>
</section>

<section class="about" id="over-het-bos">
  <div class="wrap split">
    <div class="about-img reveal">
      <img src="/img/boompjes-planten-1.jpg" alt="Vrijwilligers tijdens een plantdag in het bos" loading="lazy">
    </div>
    <div class="about-text reveal">
      <p class="eyebrow dark">Over het bos</p>
      <h2>Bijna een eeuw familiegeschiedenis, nu met een blik op de toekomst</h2>
      <p>Het Van Wezelbos is al bijna een eeuw een deel van onze familiegeschiedenis. Wat ooit begon als een aangeplant dennenbos voor de mijnbouw, willen we de komende decennia stap voor stap omvormen tot een gezond, klimaatbestendig loofbos vol leven.</p>
      <p>Onze visie gaat verder dan alleen het planten van bomen. We willen biodiversiteit vergroten, ruimte geven aan vogels, insecten en planten, maar ook aan stilte, verwondering en educatie. Het bos wordt een gemeenschappelijke plek: een levende klas voor jong en oud, een ontmoetingsplek voor familie en vrienden, en een erfgoed dat we zorgvuldig doorgeven.</p>
      <ul class="pillars">
        <li><b>Ecologie</b><span>Exoten verwijderen, inheemse soorten aanplanten.</span></li>
        <li><b>Gemeenschap</b><span>Een levende klas en ontmoetingsplek.</span></li>
        <li><b>Erfgoed</b><span>Rust, bezinning en voedselbomen voor later.</span></li>
      </ul>
    </div>
  </div>
</section>

<section class="news">
  <div class="wrap">
    <div class="head reveal">
      <div>
        <p class="eyebrow dark">Nieuws uit het bos</p>
        <h2>Laatste werkzaamheden</h2>
      </div>
      <a class="link" href="/blog/">Alle berichten →</a>
    </div>
    <div class="cards">
{cards}
    </div>
  </div>
</section>

<section class="plan">
  <div class="wrap plan-in reveal">
    <div>
      <p class="eyebrow">Bosbeheerplan</p>
      <h2>Dertig jaar aan doelen en acties</h2>
      <p>Van het verwijderen van exoten en het aanplanten van nieuwe soorten tot plekken voor rust en bezinning: in het beheerplan zoeken we de balans tussen ecologie, cultuur, spiritualiteit en praktische waarde.</p>
    </div>
    <a class="btn light" href="{PDF}" target="_blank" rel="noopener">Download het beheerplan <small>PDF · 16 MB</small></a>
  </div>
</section>
"""
    return layout(NAME, body, path="/", home=True)


def blog_index():
    cards = "\n".join(card(p) for p in posts)
    body = f"""
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow dark">Nieuws</p>
    <h1>Werkzaamheden in het bos</h1>
    <p class="lede dark">Een logboek van wat we in het Van Wezelbos doen: van rododendrons zagen tot boompjes planten.</p>
  </div>
</section>
<section class="news list">
  <div class="wrap"><div class="cards">
{cards}
  </div></div>
</section>
"""
    return layout("Nieuws", body, path="/blog/",
                  desc="Alle berichten over de werkzaamheden in het Van Wezelbos.")


def post_page(i, p):
    text = (ROOT / "content/posts" / f"{p['slug']}.html").read_text()
    gallery = ""
    if p["gallery"]:
        figs = "".join(f'<img src="/img/{g}" alt="{e(a)}" loading="lazy">' for g, a in p["gallery"])
        gallery = f'<div class="gallery n{len(p["gallery"])}">{figs}</div>'
    nxt = posts[i + 1] if i + 1 < len(posts) else None
    prv = posts[i - 1] if i > 0 else None
    nav = ""
    if prv:
        nav += f'<a href="/blog/{prv["slug"]}/"><small>← Nieuwer</small>{e(prv["title"])}</a>'
    else:
        nav += "<span></span>"
    if nxt:
        nav += f'<a class="r" href="/blog/{nxt["slug"]}/"><small>Ouder →</small>{e(nxt["title"])}</a>'
    body = f"""
<article class="post">
  <header class="post-head">
    <div class="wrap narrow">
      <a class="back" href="/blog/">← Alle berichten</a>
      <span class="tag">Werkzaamheden · {e(p['label'])}</span>
      <h1>{e(p['title'])}</h1>
    </div>
  </header>
  <div class="wrap post-hero"><img src="/img/{p['hero']}" alt="{e(p['heroAlt'])}" fetchpriority="high"></div>
  <div class="wrap narrow prose">
{text}
  </div>
  <div class="wrap">{gallery}</div>
  <nav class="wrap narrow pager" aria-label="Meer berichten">{nav}</nav>
</article>
"""
    return layout(p["title"], body, path=f"/blog/{p['slug']}/", desc=p["excerpt"],
                  image=f"/img/{p['hero']}", og="article")


def write(path, content):
    f = PUB / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content)


write("index.html", home())
write("blog/index.html", blog_index())
for i, p in enumerate(posts):
    write(f"blog/{p['slug']}/index.html", post_page(i, p))

write("404.html", layout("Pagina niet gevonden", """
<section class="page-head"><div class="wrap">
  <p class="eyebrow dark">404</p><h1>Hier staat geen boom</h1>
  <p class="lede dark">Deze pagina bestaat niet (meer). Misschien vind je wat je zoekt op de homepage of bij het nieuws.</p>
  <div class="cta"><a class="btn dark" href="/">Naar home</a> <a class="btn ghost dark" href="/blog/">Nieuws</a></div>
</div></section>""", path="/404"))

urls = ["/", "/blog/"] + [f"/blog/{p['slug']}/" for p in posts]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "\n".join(f"  <url><loc>{SITE}{u}</loc></url>" for u in urls) + "\n</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
print(f"Klaar: {len(urls)} pagina's in {PUB}")
