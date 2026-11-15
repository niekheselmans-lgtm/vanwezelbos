#!/usr/bin/env python3
"""Genereert de statische pagina's in public/ vanuit content/posts/*.md.

Draait automatisch op Vercel bij elke wijziging (zie vercel.json).
Lokaal:  python3 scripts/build.py

Berichten worden beheerd via /admin (Decap CMS) en staan als Markdown in
content/posts/. Bovenaan elk bestand staat: category, date, title, image.
"""
import html
import re
from pathlib import Path

try:  # Pillow is optioneel: zonder blijven foto's gewoon in originele grootte
    from PIL import Image, ImageOps
except Exception:  # pragma: no cover
    Image = None

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
SITE = "https://www.vanwezelbos.nl"
NAME = "Het Van Wezelbos"
DESC = ("Het Van Wezelbos is een familiebos dat stap voor stap wordt omgevormd tot een "
        "gezond, klimaatbestendig loofbos vol leven. Volg het beheerplan 2024–2050.")
PDF = "/documenten/bosbeheerplan-van-wezel-bos.pdf"
CATEGORIES = {"werkzaamheden": "Werkzaamheden", "algemeen": "Algemeen"}
MONTHS = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
          "augustus", "september", "oktober", "november", "december"]
e = html.escape


# ---------------------------------------------------------------- afbeeldingen
def opt(src, width):
    """Geef een verkleinde versie van een foto in /img/ terug (indien mogelijk)."""
    if Image is None or not src.startswith("/img/") or "/_opt/" in src:
        return src
    f = PUB / src.lstrip("/")
    if not f.exists() or f.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
        return src
    out = PUB / "img" / "_opt" / f"{f.stem}-{width}.jpg"
    try:
        if not out.exists() or out.stat().st_mtime < f.stat().st_mtime:
            with Image.open(f) as im:
                im = ImageOps.exif_transpose(im)
                if im.width <= width:
                    return src
                im = im.convert("RGB")
                im.thumbnail((width, width * 4))
                out.parent.mkdir(parents=True, exist_ok=True)
                im.save(out, "JPEG", quality=80, optimize=True, progressive=True)
        return f"/img/_opt/{out.name}"
    except Exception:
        return src


# ------------------------------------------------------------------- markdown
def inline(text):
    t = e(text, quote=False)
    t = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)",
               lambda m: f'<img src="{opt(m.group(2), 1600)}" alt="{m.group(1)}" loading="lazy">', t)
    t = re.sub(r"\[([^\]]+)\]\(((?:https?://|mailto:|/|#)[^)\s]*)\)",
               lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: f"<strong>{m.group(1) or m.group(2)}</strong>", t)
    t = re.sub(r"(?<![\*\w])\*(?!\s)(.+?)(?<!\s)\*(?![\*\w])", r"<em>\1</em>", t)
    t = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", r"<em>\1</em>", t)
    return t


UL_RE = re.compile(r"^\s*[-*+]\s+")
OL_RE = re.compile(r"^\s*\d+[.)]\s+")


def md_to_html(md):
    out = []
    for block in re.split(r"\n\s*\n", md.replace("\r\n", "\n").strip()):
        block = block.strip("\n")
        if not block.strip():
            continue
        lines = block.split("\n")
        m = re.match(r"^(#{1,6})\s+(.*)$", lines[0])
        if m and len(lines) == 1:
            level = 2 if len(m.group(1)) <= 2 else 3
            out.append(f"<h{level}>{inline(m.group(2).strip())}</h{level}>")
        elif re.fullmatch(r"[-*_]{3,}", block.strip()):
            out.append("<hr>")
        elif re.fullmatch(r"!\[[^\]]*\]\([^)\s]+\)", block.strip()):
            m = re.match(r"!\[([^\]]*)\]\(([^)\s]+)\)", block.strip())
            cap = f"<figcaption>{e(m.group(1))}</figcaption>" if m.group(1) else ""
            out.append(f'<figure><img src="{opt(m.group(2), 1600)}" alt="{e(m.group(1))}" loading="lazy">{cap}</figure>')
        elif all(re.match(r"^\s*[-*+]\s+", l) for l in lines):
            items = "".join("<li>" + inline(UL_RE.sub("", l)) + "</li>" for l in lines)
            out.append(f"<ul>{items}</ul>")
        elif all(re.match(r"^\s*\d+[.)]\s+", l) for l in lines):
            items = "".join("<li>" + inline(OL_RE.sub("", l)) + "</li>" for l in lines)
            out.append(f"<ol>{items}</ol>")
        elif all(l.startswith(">") for l in lines):
            body = " ".join(l.lstrip("> ").strip() for l in lines)
            out.append(f"<blockquote><p>{inline(body)}</p></blockquote>")
        else:
            out.append(f"<p>{inline(' '.join(l.strip() for l in lines))}</p>")
    return "\n".join(out)


def plain(md):
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"[#*_`>]", "", t)
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------------------------------------------- bestanden
def parse_post(path):
    raw = path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.S)
    if not m:
        raise SystemExit(f"{path.name}: frontmatter ontbreekt")
    meta = {}
    for line in m.group(1).split("\n"):
        k, _, v = line.partition(":")
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1].replace('\\"', '"').replace("\\\\", "\\") if v[0] == '"' else v[1:-1].replace("''", "'")
        meta[k.strip()] = v
    body = m.group(2).strip()
    date = (meta.get("date") or "1970-01-01")[:10]
    y, mo, d = (int(x) for x in date.split("-"))
    cat = meta.get("category", "werkzaamheden")
    first = next((b for b in re.split(r"\n\s*\n", body) if plain(b)), "")
    ex = plain(first)
    if len(ex) > 170:
        ex = ex[:170].rsplit(" ", 1)[0].rstrip(",.;:–-") + "…"
    title = meta.get("title", path.stem)
    return {
        "slug": path.stem, "title": title, "date": date, "cat": cat,
        "cat_label": CATEGORIES.get(cat, cat.capitalize()),
        "label": f"{d} {MONTHS[mo - 1]} {y}",
        "image": meta.get("image") or "/img/toekomstbomen-1.jpg",
        "excerpt": ex, "body": body,
    }


posts = sorted((parse_post(p) for p in (ROOT / "content/posts").glob("*.md")),
               key=lambda p: (p["date"], p["slug"]), reverse=True)


# -------------------------------------------------------------------- layout
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
<link href="https://fonts.googleapis.com/css2?family=Carlito:ital,wght@0,400;0,700;1,400;1,700&display=swap" rel="stylesheet">
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
    return f"""<a class="card reveal" href="/blog/{p['slug']}/" data-cat="{e(p['cat'])}">
  <div class="card-img"><img src="{opt(p['image'], 800)}" alt="{e(p['title'])}" loading="lazy"></div>
  <div class="card-body">
    <span class="tag">{e(p['cat_label'])} · {e(p['label'])}</span>
    <h3>{e(p['title'])}</h3>
    <p>{e(p['excerpt'])}</p>
    <span class="more">Lees verder <b aria-hidden="true">→</b></span>
  </div>
</a>"""


def home():
    cards = "\n".join(card(p) for p in posts[:3])
    body = f"""
<section class="hero">
  <img src="{opt('/img/toekomstbomen-1.jpg', 1800)}" alt="Rododendrons en dennen in het Van Wezelbos" fetchpriority="high">
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
      <img src="{opt('/img/boompjes-planten-1.jpg', 1200)}" alt="Vrijwilligers tijdens een plantdag in het bos" loading="lazy">
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
        <h2>Laatste berichten</h2>
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
    used = [c for c in CATEGORIES if any(p["cat"] == c for p in posts)]
    filters = ""
    if len(used) > 1:
        chips = '<button class="chip on" data-filter="all">Alle</button>' + "".join(
            f'<button class="chip" data-filter="{c}">{CATEGORIES[c]}</button>' for c in used)
        filters = f'<div class="filters" role="group" aria-label="Filter op categorie">{chips}</div>'
    body = f"""
<section class="page-head">
  <div class="wrap">
    <p class="eyebrow dark">Nieuws</p>
    <h1>Berichten uit het bos</h1>
    <p class="lede dark">Een logboek van wat we in het Van Wezelbos doen: van rododendrons zagen tot boompjes planten.</p>
    {filters}
  </div>
</section>
<section class="news list">
  <div class="wrap"><div class="cards">
{cards}
  </div></div>
</section>
"""
    return layout("Nieuws", body, path="/blog/",
                  desc="Alle berichten over het Van Wezelbos.")


def post_page(i, p):
    hero = f'<div class="wrap post-hero"><img src="{opt(p["image"], 1800)}" alt="{e(p["title"])}" fetchpriority="high"></div>'
    nxt = posts[i + 1] if i + 1 < len(posts) else None
    prv = posts[i - 1] if i > 0 else None
    nav = (f'<a href="/blog/{prv["slug"]}/"><small>← Nieuwer</small>{e(prv["title"])}</a>' if prv else "<span></span>")
    if nxt:
        nav += f'<a class="r" href="/blog/{nxt["slug"]}/"><small>Ouder →</small>{e(nxt["title"])}</a>'
    body = f"""
<article class="post">
  <header class="post-head">
    <div class="wrap narrow">
      <a class="back" href="/blog/">← Alle berichten</a>
      <span class="tag">{e(p['cat_label'])} · {e(p['label'])}</span>
      <h1>{e(p['title'])}</h1>
    </div>
  </header>
  {hero}
  <div class="wrap narrow prose">
{md_to_html(p['body'])}
  </div>
  <nav class="wrap narrow pager" aria-label="Meer berichten">{nav}</nav>
</article>
"""
    return layout(p["title"], body, path=f"/blog/{p['slug']}/", desc=p["excerpt"] or DESC,
                  image=p["image"], og="article")


def write(path, content):
    f = PUB / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")


# oude, niet meer bestaande berichten opruimen
live = {p["slug"] for p in posts}
blog_dir = PUB / "blog"
if blog_dir.exists():
    for d in blog_dir.iterdir():
        if d.is_dir() and d.name not in live:
            for f in d.rglob("*"):
                if f.is_file():
                    f.unlink()
            for sub in sorted(d.rglob("*"), reverse=True):
                sub.rmdir()
            d.rmdir()

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
write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /admin/\nSitemap: {SITE}/sitemap.xml\n")
print(f"Klaar: {len(urls)} pagina's, {len(posts)} berichten" + ("" if Image else " (zonder Pillow: foto's niet verkleind)"))
