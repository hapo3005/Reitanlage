from pathlib import Path
from html import escape
import json
import os
import re

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '_site'
TOKEN = os.environ.get('GITHUB_SHA', 'local-audit')[:12]
SITE_URL = os.environ.get('SITE_URL', 'https://hapo3005.github.io/Reitanlage/').rstrip('/') + '/'

EXTRA_IMAGES = (
    'images/reistunde1.png',
    'images/flyerferienreitskurs2.png',
    'images/frohefeiertage.png',
)

# These sources are genuinely small. A restrained 2x Lanczos enlargement plus
# a mild unsharp mask gives them a cleaner presentation on modern screens
# without pretending to reconstruct detail that is not in the original.
UPSCALE_IMAGES = (
    'images/eventbild3.png',
    'images/eventbild4.png',
    'images/schulpferd1.png',
    'images/schulpferd2.png',
    'images/schulpferd3.png',
)


def webp_name(src: str) -> str:
    return str(Path(src).with_suffix('.webp')).replace('\\', '/')


def variant_name(src: str, width: int) -> str:
    p = Path(src)
    return str(p.with_name(f'{p.stem}-{width}.webp')).replace('\\', '/')


def save_webp(im: Image.Image, dest: Path, *, quality=87, lossless=False):
    dest.parent.mkdir(parents=True, exist_ok=True)
    mode = 'RGBA' if 'A' in im.getbands() else 'RGB'
    im = im.convert(mode)
    kwargs = {'format': 'WEBP', 'method': 6}
    if lossless:
        kwargs['lossless'] = True
    else:
        kwargs['quality'] = quality
    im.save(dest, **kwargs)


def upscale_photo(source: Path, dest: Path):
    im = Image.open(source)
    width, height = im.size
    enlarged = im.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
    enlarged = enlarged.filter(ImageFilter.UnsharpMask(radius=1.0, percent=105, threshold=3))
    save_webp(enlarged, dest, quality=89)


if not OUT.exists():
    raise RuntimeError('Run build-release.py before build-journal.py')

# The journal shares the production stylesheet; its page-specific rules are
# appended at build time so the public site still ships only one CSS file.
site_css = OUT / 'site.css'
site_css.write_text(
    site_css.read_text(encoding='utf-8')
    + '\n\n/* ===== journal.css ===== */\n'
    + (ROOT / 'journal.css').read_text(encoding='utf-8').rstrip()
    + '\n',
    encoding='utf-8',
)

# Restore more of the original site's imagery for the journal and optimize it.
for src in EXTRA_IMAGES:
    source = ROOT / src
    if not source.exists():
        raise FileNotFoundError(source)
    im = Image.open(source)
    lossless = 'flyer' in source.name.lower()
    save_webp(im, OUT / webp_name(src), quality=88, lossless=lossless)

    # The journal hero benefits from real responsive variants.
    if source.name == 'reistunde1.png':
        for width in (480, 720, 960, 1280):
            if width >= im.width:
                continue
            height = round(im.height * width / im.width)
            resized = im.resize((width, height), Image.Resampling.LANCZOS)
            save_webp(resized, OUT / variant_name(src, width), quality=85)

# Replace small public photos with restrained 2x display versions. Their aspect
# ratio stays identical, so existing layouts and image focal points are stable.
for src in UPSCALE_IMAGES:
    source = ROOT / src
    if source.exists():
        upscale_photo(source, OUT / webp_name(src))


def optimized_news_image(src: str) -> str:
    if src.startswith('images/'):
        return webp_name(src)
    return src


def news_href(link: str) -> str:
    if not link:
        return 'index.html#kontakt'
    return f'index.html{link}' if link.startswith('#') else link


def news_meta(item):
    values = [item.get('category'), item.get('meta')]
    return ' · '.join(escape(v) for v in values if v)


def render_current_news(data):
    items = [i for i in data.get('items', []) if i.get('title') and i.get('text')][:3]
    if not items:
        return '<p>Aktuell sind keine Meldungen veröffentlicht. Termine bitte direkt bei Carmen erfragen.</p>'

    featured = items[0]
    fit_class = ' is-contain' if featured.get('imageFit') == 'contain' else ''
    image = optimized_news_image(featured.get('image', ''))
    link = news_href(featured.get('link', '#kontakt'))
    main = f'''<div class="journal-current-grid">
      <article class="journal-current-main">
        <figure class="{fit_class.strip()}"><img src="{escape(image)}" alt="{escape(featured.get('alt','Aktuelles von der Reitanlage Eichhorn-Nels'))}" loading="lazy" decoding="async"></figure>
        <div class="journal-current-copy"><p class="journal-meta">{news_meta(featured)}</p><h3>{escape(featured['title'])}</h3><p>{escape(featured['text'])}</p><a class="news-link" href="{escape(link)}">{escape(featured.get('linkText','Anfragen'))}</a></div>
      </article>'''

    sides = []
    for item in items[1:]:
        image = optimized_news_image(item.get('image', ''))
        link = news_href(item.get('link', '#kontakt'))
        sides.append(f'''<article class="journal-current-side">
          <figure><img src="{escape(image)}" alt="{escape(item.get('alt','Aktuelles von der Reitanlage Eichhorn-Nels'))}" loading="lazy" decoding="async"></figure>
          <div class="journal-current-side-copy"><p class="journal-meta">{news_meta(item)}</p><h3>{escape(item['title'])}</h3><p>{escape(item['text'])}</p><a class="news-link" href="{escape(link)}">{escape(item.get('linkText','Anfragen'))}</a></div>
        </article>''')
    return main + '<div class="journal-current-side-list">' + ''.join(sides) + '</div></div>'


news = json.loads((ROOT / 'aktuelles.json').read_text(encoding='utf-8'))
html = (ROOT / 'aktuelles.html').read_text(encoding='utf-8')
html = html.replace('<!-- CURRENT_NEWS -->', render_current_news(news))

# All local journal imagery is served in the optimized release format.
all_local_images = set(EXTRA_IMAGES) | set(UPSCALE_IMAGES) | {
    'images/reitbeteiligung1.png',
    'images/eventbild1.png',
    'images/eventbild2.png',
    'images/familieanuth.png',
    'images/flyerferienreitkurs.png',
}
for src in all_local_images:
    html = html.replace(src, webp_name(src))

# Responsive hero delivery; the full WebP remains the final srcset candidate.
hero_src = webp_name('images/reistunde1.png')
hero_source = Image.open(ROOT / 'images/reistunde1.png')
hero_candidates = []
for width in (480, 720, 960, 1280):
    if width < hero_source.width:
        hero_candidates.append(f'{variant_name("images/reistunde1.png", width)} {width}w')
hero_candidates.append(f'{hero_src} {hero_source.width}w')
html = html.replace(
    f'<img src="{hero_src}" alt="Reitstunde auf der Reitanlage Eichhorn-Nels">',
    f'<img src="{hero_src}" srcset="{", ".join(hero_candidates)}" sizes="(max-width:820px) 100vw, 56vw" alt="Reitstunde auf der Reitanlage Eichhorn-Nels" width="{hero_source.width}" height="{hero_source.height}" fetchpriority="high" decoding="async">',
    1,
)

# Add intrinsic sizes to the remaining journal images and keep them lazy.
def improve_journal_img(match):
    tag = match.group(0)
    if 'width=' in tag:
        return tag
    src_match = re.search(r'src="([^"]+)"', tag)
    if not src_match:
        return tag
    webp = src_match.group(1)
    source_rel = None
    for src in all_local_images:
        if webp_name(src) == webp:
            source_rel = src
            break
    if not source_rel:
        return tag
    im = Image.open(ROOT / source_rel)
    width, height = im.size
    if source_rel in UPSCALE_IMAGES:
        width *= 2
        height *= 2
    tag = tag[:-1] + f' width="{width}" height="{height}"'
    if 'loading=' not in tag:
        tag += ' loading="lazy"'
    if 'decoding=' not in tag:
        tag += ' decoding="async"'
    return tag + '>'

html = re.sub(r'<img\b[^>]*>', improve_journal_img, html)

# Canonicals, social metadata and structured data follow SITE_URL just like the
# landing page. This keeps a later domain move configuration-only.
page_url = SITE_URL + 'aktuelles.html'
html = re.sub(r'<link rel="canonical" href="[^"]+">', f'<link rel="canonical" href="{page_url}">', html, count=1)
html = re.sub(r'<meta property="og:image" content="[^"]+">', f'<meta property="og:image" content="{SITE_URL}social-preview.jpg">', html, count=1)
if 'property="og:url"' not in html:
    html = html.replace('<meta property="og:type" content="website">', f'<meta property="og:type" content="website"><meta property="og:url" content="{page_url}"><meta property="og:site_name" content="Reitanlage Eichhorn-Nels">', 1)
html = html.replace('https://hapo3005.github.io/Reitanlage/aktuelles.html', page_url)
html = html.replace('https://hapo3005.github.io/Reitanlage/', SITE_URL)
html = re.sub(r'href="site\.css(?:\?v=[^"]*)?"', f'href="site.css?v={TOKEN}"', html)
html = re.sub(r'src="site\.js(?:\?v=[^"]*)?"', f'src="site.js?v={TOKEN}"', html)
(OUT / 'aktuelles.html').write_text(html, encoding='utf-8')

# The start page remains a concise teaser, but now points clearly to the full
# journal. Navigation also opens the dedicated page.
index_path = OUT / 'index.html'
index = index_path.read_text(encoding='utf-8')
index = index.replace('<a href="#aktuelles">Aktuelles</a>', '<a href="aktuelles.html">Aktuelles</a>', 1)
marker = '<p class="updated" data-news-updated></p>'
if 'Alle Neuigkeiten &amp; Rückblicke' not in index and 'Alle Neuigkeiten & Rückblicke' not in index:
    index = index.replace(marker, marker + '<p class="news-all-link"><a href="aktuelles.html">Alle Neuigkeiten &amp; Rückblicke</a></p>', 1)
index_path.write_text(index, encoding='utf-8')

# Make the journal discoverable for search engines.
sitemap_path = OUT / 'sitemap.xml'
sitemap = sitemap_path.read_text(encoding='utf-8')
entry = f'  <url><loc>{page_url}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>\n'
if page_url not in sitemap:
    sitemap = sitemap.replace('</urlset>', entry + '</urlset>')
sitemap_path.write_text(sitemap, encoding='utf-8')

print('Built Aktuelles & Hofleben journal and enhanced small imagery.')
