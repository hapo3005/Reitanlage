from pathlib import Path
import json
import os
import re
import shutil

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '_site'
TOKEN = os.environ.get('GITHUB_SHA', 'local-audit')[:12]
SITE_URL = os.environ.get('SITE_URL', 'https://hapo3005.github.io/Reitanlage/').rstrip('/') + '/'

CSS_PARTS = [
    'rebuild-base.css',
    'hero-mobile.css',
    'responsive.css',
    'mobile-safety.css',
    'contact-finish.css',
    'site-finish.css',
    'mobile-final-20260826.css',
    'news-expanded.css',
    'footer-fix.css',
    'photo-zoom.css',
    'ui-polish.css',
    'ui-refine.css',
    'news-zoom-polish.css',
    'news-cta-polish.css',
    'hero-premium-20260827.css',
]

IMAGE_META = {
    'images/reitbeteiligung1.png': (1471, 1962),
    'images/eventbild1.png': (828, 552),
    'images/eventbild2.png': (828, 552),
    'images/eventbild3.png': (380, 214),
    'images/eventbild4.png': (200, 267),
    'images/familieanuth.png': (1200, 1600),
    'images/schulpferd1.png': (200, 355),
    'images/schulpferd2.png': (340, 255),
    'images/schulpferd3.png': (340, 255),
    'images/flyerferienreitkurs.png': (1080, 1080),
}

ACTIVE_IMAGES = tuple(IMAGE_META)
RESPONSIVE = {
    'images/reitbeteiligung1.png': (480, 720, 960, 1200),
    'images/familieanuth.png': (480, 720, 960),
}


def optimized_name(src: str) -> str:
    p = Path(src)
    return str(p.with_suffix('.webp')).replace('\\', '/')


def variant_name(src: str, width: int) -> str:
    p = Path(src)
    return str(p.with_name(f'{p.stem}-{width}.webp')).replace('\\', '/')


def save_webp(im: Image.Image, dest: Path, *, lossless=False, quality=86):
    dest.parent.mkdir(parents=True, exist_ok=True)
    mode = 'RGBA' if 'A' in im.getbands() else 'RGB'
    im = im.convert(mode)
    kwargs = {'format': 'WEBP', 'method': 6}
    if lossless:
        kwargs['lossless'] = True
    else:
        kwargs['quality'] = quality
    im.save(dest, **kwargs)


# Build into a clean deployment directory. Source and maintenance files are not
# published, which keeps the production surface small and predictable.
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

# Compile the validated CSS cascade into one production file.
css_chunks = []
for name in CSS_PARTS:
    path = ROOT / name
    css_chunks.append(f'/* ===== {name} ===== */\n{path.read_text(encoding="utf-8").rstrip()}\n')
css_chunks.append(
    '/* ===== release guardrails ===== */\n'
    'html,body{max-width:100%;}\n'
    'img{max-width:100%;}\n'
    '.hero-image img{object-position:52% 48%}\n'
    '.contact.contact-editorial address p:nth-child(4) a::after{content:"  ·  Route öffnen"!important}\n'
    '@media(max-width:820px){.hero-copy,.hero-copy h1{color:#fff}.hero-copy .kicker,.hero-copy h1 em{color:#eadbc2}}\n'
)
(OUT / 'site.css').write_text('\n'.join(css_chunks), encoding='utf-8')

# Bundle JS plus keyboard/focus safeguards.
js_parts = ['script.js', 'accessibility-finish.js']
site_js = '\n\n'.join((ROOT / name).read_text(encoding='utf-8').rstrip() for name in js_parts) + '\n'
(OUT / 'site.js').write_text(site_js, encoding='utf-8')

# Generate optimized WebP copies for every image used by the public site.
for src in ACTIVE_IMAGES:
    source = ROOT / src
    if not source.exists():
        raise FileNotFoundError(source)
    im = Image.open(source)
    lossless = source.name == 'flyerferienreitkurs.png'
    save_webp(im, OUT / optimized_name(src), lossless=lossless, quality=86)

    for width in RESPONSIVE.get(src, ()):
        if width >= im.width:
            continue
        height = round(im.height * width / im.width)
        resized = im.resize((width, height), Image.Resampling.LANCZOS)
        save_webp(resized, OUT / variant_name(src, width), quality=84)

# Social sharing gets a purpose-built 1200 × 630 crop rather than a vertical
# source image. No text is baked into the image, so previews remain timeless.
hero = Image.open(ROOT / 'images/reitbeteiligung1.png').convert('RGB')
social = ImageOps.fit(hero, (1200, 630), method=Image.Resampling.LANCZOS, centering=(0.5, 0.38))
social.save(OUT / 'social-preview.jpg', 'JPEG', quality=88, optimize=True, progressive=True)

favicon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" fill="#173027"/>
<path d="M14 17h15v4H19v8h9v4h-9v10h10v4H14V17Zm22 0h4l10 21V17h4v30h-4L40 26v21h-4V17Z" fill="#f4f0e7"/>
</svg>\n'''
(OUT / 'favicon.svg').write_text(favicon, encoding='utf-8')
manifest = {
    'name': 'Reitanlage Eichhorn-Nels',
    'short_name': 'Eichhorn-Nels',
    'start_url': './',
    'display': 'browser',
    'background_color': '#f4f0e7',
    'theme_color': '#173027',
    'icons': [{'src': 'favicon.svg', 'sizes': 'any', 'type': 'image/svg+xml'}],
}
(OUT / 'site.webmanifest').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Build the landing page from source.
html = (ROOT / 'index.html').read_text(encoding='utf-8')
html = re.sub(r'<section class="legal" id="impressum">.*?</section>', '', html, flags=re.S)
html = html.replace('href="#impressum">Impressum</a>', 'href="impressum.html">Impressum</a>')
html = html.replace('href="#datenschutz">Datenschutz</a>', 'href="datenschutz.html">Datenschutz</a>')
html = html.replace('<span>Mehr Einblicke</span><a href="https://www.facebook.com/groups/403038393066632/"', '<span>Facebook</span><a href="https://www.facebook.com/groups/403038393066632/"')
html = html.replace('Facebook-Gruppe ↗', 'Facebook-Gruppe').replace('Nach oben ↑', 'Nach oben')
html = html.replace('>Reitstunde anfragen</a>', '>Unverbindlich anfragen</a>', 1)
html = html.replace('>WhatsApp schreiben</a>', '>Per WhatsApp schreiben</a>', 1)

# One CSS/JS pair, plus icon/manifest metadata.
html = re.sub(r'<link rel="stylesheet" href="[^"]+\.css(?:\?v=[^"]*)?">', '', html)
html = re.sub(r'<link rel="preload" as="image" href="[^"]+">', '', html)
head_assets = (
    f'<link rel="preload" as="image" href="images/reitbeteiligung1-960.webp" type="image/webp">'
    f'<link rel="stylesheet" href="site.css?v={TOKEN}">'
    '<link rel="icon" href="favicon.svg" type="image/svg+xml">'
    '<link rel="manifest" href="site.webmanifest">'
)
html = html.replace('</head>', head_assets + '\n</head>', 1)

# Canonical URL and sharing metadata are generated from SITE_URL, making a
# future domain move a configuration change rather than a code rewrite.
html = re.sub(r'<link rel="canonical" href="[^"]+">', f'<link rel="canonical" href="{SITE_URL}">', html, count=1)
html = re.sub(r'<meta property="og:image" content="[^"]+">', f'<meta property="og:image" content="{SITE_URL}social-preview.jpg">', html, count=1)
if 'property="og:url"' not in html:
    html = html.replace('<meta property="og:type" content="website">', f'<meta property="og:type" content="website"><meta property="og:url" content="{SITE_URL}"><meta property="og:site_name" content="Reitanlage Eichhorn-Nels">', 1)
else:
    html = re.sub(r'<meta property="og:url" content="[^"]+">', f'<meta property="og:url" content="{SITE_URL}">', html, count=1)
for prop, value in [
    ('og:image:width', '1200'),
    ('og:image:height', '630'),
    ('og:image:alt', 'Pferd im Abendlicht auf der Reitanlage Eichhorn-Nels'),
]:
    if f'property="{prop}"' not in html:
        html = html.replace('<meta name="twitter:card" content="summary_large_image">', f'<meta property="{prop}" content="{value}"><meta name="twitter:card" content="summary_large_image">', 1)
if 'name="twitter:title"' not in html:
    twitter = (
        '<meta name="twitter:title" content="Reitunterricht &amp; Pferdepension bei Wittlich | Eichhorn-Nels">'
        '<meta name="twitter:description" content="Reitunterricht für Kinder, Jugendliche und Erwachsene in Minderlittgen – dazu Pferdepension, Beritt und Ausritte.">'
        f'<meta name="twitter:image" content="{SITE_URL}social-preview.jpg">'
        '<meta name="twitter:image:alt" content="Pferd im Abendlicht auf der Reitanlage Eichhorn-Nels">'
    )
    html = html.replace('<meta name="twitter:card" content="summary_large_image">', '<meta name="twitter:card" content="summary_large_image">' + twitter, 1)
else:
    html = re.sub(r'<meta name="twitter:image" content="[^"]+">', f'<meta name="twitter:image" content="{SITE_URL}social-preview.jpg">', html, count=1)

# Keep structured data synchronized with the active deployment URL and the
# public Facebook channel already used by the page.
def update_ld(match):
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return match.group(0)
    data['url'] = SITE_URL
    data['sameAs'] = ['https://www.facebook.com/groups/403038393066632/']
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '</script>'

html = re.sub(r'<script type="application/ld\+json">(.*?)</script>', update_ld, html, flags=re.S, count=1)

# Optimize static image delivery and keep intrinsic dimensions to avoid layout
# shifts. Hero/contact get responsive sources; all other public images use WebP.
def improve_img(match):
    tag = match.group(0)
    src_match = re.search(r'src="([^"]+)"', tag)
    if not src_match:
        return tag
    src = src_match.group(1)
    if src not in IMAGE_META:
        return tag
    width, height = IMAGE_META[src]
    context = html[max(0, match.start() - 180):match.start()]
    original = src
    if src == 'images/reitbeteiligung1.png' and 'hero-image' in context:
        tag = tag.replace(f'src="{src}"', 'src="images/reitbeteiligung1-960.webp"')
        candidates = [f'{variant_name(src, w)} {w}w' for w in RESPONSIVE[src]]
        candidates.append(f'{optimized_name(src)} {width}w')
        tag = tag[:-1] + f' srcset="{", ".join(candidates)}" sizes="(max-width:820px) 100vw, 55vw">'
    elif src == 'images/familieanuth.png':
        tag = tag.replace(f'src="{src}"', 'src="images/familieanuth-720.webp"')
        candidates = [f'{variant_name(src, w)} {w}w' for w in RESPONSIVE[src]]
        candidates.append(f'{optimized_name(src)} {width}w')
        tag = tag[:-1] + f' srcset="{", ".join(candidates)}" sizes="(max-width:820px) 100vw, 52vw">'
    else:
        tag = tag.replace(f'src="{src}"', f'src="{optimized_name(src)}"')
    if not re.search(r'\bwidth="', tag):
        tag = tag[:-1] + f' width="{width}" height="{height}">'
    if 'decoding=' not in tag:
        tag = tag[:-1] + ' decoding="async">'
    if original == 'images/reitbeteiligung1.png' and 'hero-image' in context:
        if 'fetchpriority=' not in tag:
            tag = tag[:-1] + ' fetchpriority="high">'
    elif 'loading=' not in tag:
        tag = tag[:-1] + ' loading="lazy">'
    return tag

html = re.sub(r'<img\b[^>]*>', improve_img, html)
html = re.sub(r'<script src="(?:script|site)\.js(?:\?v=[^"]*)?"></script>', f'<script src="site.js?v={TOKEN}"></script>', html)
(OUT / 'index.html').write_text(html, encoding='utf-8')

# News source remains easy to edit; the deployment copy points at optimized
# media without making maintainers type generated file names.
news = json.loads((ROOT / 'aktuelles.json').read_text(encoding='utf-8'))
for item in news.get('items', []):
    src = item.get('image')
    if src in IMAGE_META:
        item['image'] = optimized_name(src)
(OUT / 'aktuelles.json').write_text(json.dumps(news, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Dedicated legal pages retain their own restrained stylesheet and share the
# same icon/manifest. Their canonical URLs also follow SITE_URL.
shutil.copy2(ROOT / 'legal-page.css', OUT / 'legal-page.css')
for filename in ('impressum.html', 'datenschutz.html'):
    text = (ROOT / filename).read_text(encoding='utf-8')
    text = re.sub(r'legal-page\.css\?v=[^"]+', f'legal-page.css?v={TOKEN}', text)
    text = re.sub(r'<link rel="canonical" href="[^"]+">', f'<link rel="canonical" href="{SITE_URL}{filename}">', text, count=1)
    text = text.replace('← Zurück zur Seite', 'Zurück zur Seite')
    if 'rel="icon"' not in text:
        text = text.replace('</head>', '<link rel="icon" href="favicon.svg" type="image/svg+xml"><link rel="manifest" href="site.webmanifest">\n</head>', 1)
    (OUT / filename).write_text(text, encoding='utf-8')

# Search engine files are generated so the future custom domain never inherits
# a stale GitHub Pages URL.
(OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n', encoding='utf-8')
(OUT / 'sitemap.xml').write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f'  <url><loc>{SITE_URL}</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>\n'
    f'  <url><loc>{SITE_URL}impressum.html</loc><changefreq>yearly</changefreq><priority>0.2</priority></url>\n'
    f'  <url><loc>{SITE_URL}datenschutz.html</loc><changefreq>yearly</changefreq><priority>0.2</priority></url>\n'
    '</urlset>\n',
    encoding='utf-8',
)

# A quiet branded 404 makes direct/old links fail gracefully on conventional
# static hosting as well as on Pages-compatible hosts.
not_found = f'''<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><meta name="theme-color" content="#173027"><link rel="icon" href="favicon.svg" type="image/svg+xml"><title>Seite nicht gefunden · Eichhorn-Nels</title><style>html{{background:#173027;color:#f4f0e7;font-family:Arial,sans-serif}}body{{min-height:100vh;margin:0;display:grid;place-items:center;padding:24px;box-sizing:border-box}}main{{width:min(640px,100%)}}p{{color:#d8c7aa;line-height:1.65}}h1{{font:400 clamp(2.8rem,9vw,5rem)/.98 Georgia,serif;margin:.2em 0}}a{{display:inline-block;margin-top:20px;color:#f4f0e7;text-underline-offset:5px}}</style></head><body><main><p>Reitanlage Eichhorn-Nels · Minderlittgen</p><h1>Diese Seite gibt es hier nicht.</h1><p>Über die Startseite finden Sie Reitunterricht, Pferdepension, Aktuelles, Preise und Kontakt.</p><a href="{SITE_URL}">Zur Startseite</a></main></body></html>'''
(OUT / '404.html').write_text(not_found, encoding='utf-8')

print(f'Built production site in {OUT} for {SITE_URL}')
