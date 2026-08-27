from pathlib import Path
import os
import re

ROOT = Path(__file__).resolve().parent
TOKEN = os.environ.get('GITHUB_SHA', 'local-audit')[:12]

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

# Compile the production stylesheet in the exact cascade order that has been
# validated on the live site. Source modules stay readable and maintainable.
css_chunks = []
for name in CSS_PARTS:
    path = ROOT / name
    css_chunks.append(f'/* ===== {name} ===== */\n{path.read_text(encoding="utf-8").rstrip()}\n')
css_chunks.append('/* ===== final inline adjustments ===== */\n.hero-image img{object-position:52% 48%}\n@media(max-width:820px){.hero-copy,.hero-copy h1{color:#fff}.hero-copy .kicker,.hero-copy h1 em{color:#eadbc2}}\n')
(ROOT / 'site.css').write_text('\n'.join(css_chunks), encoding='utf-8')

# Bundle the site's JS and the final keyboard/focus safeguards.
js_parts = ['script.js', 'accessibility-finish.js']
site_js = '\n\n'.join((ROOT / name).read_text(encoding='utf-8').rstrip() for name in js_parts) + '\n'
(ROOT / 'site.js').write_text(site_js, encoding='utf-8')

index = ROOT / 'index.html'
html = index.read_text(encoding='utf-8')

# The old legal blocks are build-template residue only. They must not appear in
# the published landing-page HTML now that dedicated legal pages exist.
html = re.sub(r'<section class="legal" id="impressum">.*?</section>', '', html, flags=re.S)

# Footer links must work without JavaScript.
html = html.replace('href="#impressum">Impressum</a>', 'href="impressum.html">Impressum</a>')
html = html.replace('href="#datenschutz">Datenschutz</a>', 'href="datenschutz.html">Datenschutz</a>')

# Keep the social contact label explicit and concise.
html = html.replace('<span>Mehr Einblicke</span><a href="https://www.facebook.com/groups/403038393066632/"', '<span>Facebook</span><a href="https://www.facebook.com/groups/403038393066632/"')

# One production stylesheet. Remove the old loader/direct override links first.
html = re.sub(r'<link rel="stylesheet" href="[^"]+\.css(?:\?v=[^"]*)?">', '', html)
preload = '<link rel="preload" as="image" href="images/reitbeteiligung1.png">'
style_link = f'<link rel="stylesheet" href="site.css?v={TOKEN}">'
if preload in html:
    html = html.replace(preload, preload + style_link, 1)
else:
    html = html.replace('</head>', style_link + '\n</head>', 1)

# Canonical social metadata for clean sharing/search previews.
if 'property="og:url"' not in html:
    html = html.replace(
        '<meta property="og:type" content="website">',
        '<meta property="og:type" content="website"><meta property="og:url" content="https://hapo3005.github.io/Reitanlage/"><meta property="og:site_name" content="Reitanlage Eichhorn-Nels">',
        1,
    )
if 'name="twitter:title"' not in html:
    twitter = ('<meta name="twitter:title" content="Reitunterricht &amp; Pferdepension bei Wittlich | Eichhorn-Nels">'
               '<meta name="twitter:description" content="Reitunterricht für Kinder, Jugendliche und Erwachsene in Minderlittgen – dazu Pferdepension, Beritt und Ausritte.">'
               '<meta name="twitter:image" content="https://hapo3005.github.io/Reitanlage/images/reitbeteiligung1.png">')
    html = html.replace('<meta name="twitter:card" content="summary_large_image">', '<meta name="twitter:card" content="summary_large_image">' + twitter, 1)

# Stable intrinsic sizes reduce layout shifts. Everything below the hero is
# lazy-loaded; the hero keeps high priority.
def improve_img(match):
    tag = match.group(0)
    src_match = re.search(r'src="([^"]+)"', tag)
    if not src_match:
        return tag
    src = src_match.group(1)
    dims = IMAGE_META.get(src)
    if dims:
        if not re.search(r'\bwidth="', tag):
            tag = tag[:-1] + f' width="{dims[0]}" height="{dims[1]}">'
    if 'decoding=' not in tag:
        tag = tag[:-1] + ' decoding="async">'
    if src == 'images/reitbeteiligung1.png' and 'hero-image' in html[max(0, match.start()-150):match.start()]:
        if 'fetchpriority=' not in tag:
            tag = tag[:-1] + ' fetchpriority="high">'
    elif 'loading=' not in tag:
        tag = tag[:-1] + ' loading="lazy">'
    return tag

html = re.sub(r'<img\b[^>]*>', improve_img, html)

# One production JS bundle with deterministic cache busting.
html = re.sub(r'<script src="(?:script|site)\.js(?:\?v=[^"]*)?"></script>', f'<script src="site.js?v={TOKEN}"></script>', html)

index.write_text(html, encoding='utf-8')

# Cache-bust the dedicated legal-page stylesheet as part of every release.
for name in ('impressum.html', 'datenschutz.html'):
    path = ROOT / name
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'legal-page\.css\?v=[^"]+', f'legal-page.css?v={TOKEN}', text)
    path.write_text(text, encoding='utf-8')
