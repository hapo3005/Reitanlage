from pathlib import Path
import re

from PIL import Image

ROOT = Path(__file__).resolve().parent
OUT = ROOT / '_site'
INDEX = OUT / 'index.html'
CSS = OUT / 'site.css'

index = INDEX.read_text(encoding='utf-8')

# Accessibility: let the visible wordmark provide the accessible name. The old
# aria-label omitted visible label text and therefore failed WCAG label-in-name.
index, wordmark_count = re.subn(
    r'(<header\b[^>]*>\s*<a\s+class="wordmark"\s+href="#start")\s+aria-label="[^"]+"',
    r'\1',
    index,
    count=1,
)
assert wordmark_count == 1

# Accessibility: definition-list grouping may contain dt/dd only. Keep the
# existing visual notes, but model them as additional descriptions instead of
# stray span children inside the dl grouping divs.
price_match = re.search(r'(<dl class="price-highlight"[^>]*>)(.*?)(</dl>)', index, re.S)
assert price_match
price_body, note_count = re.subn(
    r'<span>(.*?)</span>',
    r'<dd class="price-note">\1</dd>',
    price_match.group(2),
    flags=re.S,
)
assert note_count >= 4
index = index[:price_match.start()] + price_match.group(1) + price_body + price_match.group(3) + index[price_match.end():]

# The main bundle lives at the end of the document, but defer still removes it
# from Lighthouse's parser-blocking critical path and preserves DOMContentLoaded
# ordering for all existing initialization code.
index, defer_count = re.subn(
    r'<script\s+src="site\.js\?v=([^"]+)"></script>',
    r'<script defer src="site.js?v=\1"></script>',
    index,
    count=1,
)
assert defer_count == 1


def write_variant(source_rel: str, width: int, quality: int = 80) -> tuple[int, int]:
    source = ROOT / source_rel
    with Image.open(source) as image:
        source_width, source_height = image.size
        if width >= source_width:
            return source_width, source_height
        height = round(source_height * width / source_width)
        resized = image.convert('RGB').resize((width, height), Image.Resampling.LANCZOS)
        dest = OUT / 'images' / f'{Path(source_rel).stem}-{width}.webp'
        resized.save(dest, 'WEBP', quality=quality, method=6)
        return source_width, source_height


# Mobile hero: add a 400 px candidate and make preload use the same responsive
# selection algorithm as the actual img. This removes the previous 960 px
# preload + 480 px rendered-image double download on a 390 px viewport.
hero_source_width, hero_source_height = write_variant('images/reitbeteiligung1.png', 400, quality=78)
hero_candidates = [
    'images/reitbeteiligung1-400.webp 400w',
    'images/reitbeteiligung1-480.webp 480w',
    'images/reitbeteiligung1-720.webp 720w',
    'images/reitbeteiligung1-960.webp 960w',
    'images/reitbeteiligung1-1200.webp 1200w',
    f'images/reitbeteiligung1.webp {hero_source_width}w',
]
hero_srcset = ', '.join(hero_candidates)
responsive_preload = (
    '<link rel="preload" as="image" href="images/reitbeteiligung1-400.webp" '
    f'imagesrcset="{hero_srcset}" imagesizes="(max-width:820px) 100vw, 55vw" '
    'type="image/webp" fetchpriority="high">'
)
index, preload_count = re.subn(
    r'<link rel="preload" as="image" href="images/reitbeteiligung1-[^"]+" type="image/webp">',
    responsive_preload,
    index,
    count=1,
)
assert preload_count == 1

hero_img = re.search(r'<img\b(?=[^>]*\balt="Pferd im Abendlicht auf der Reitanlage Eichhorn-Nels")[^>]*>', index)
assert hero_img
hero_tag = hero_img.group(0)
hero_tag = re.sub(r'src="[^"]+"', 'src="images/reitbeteiligung1-400.webp"', hero_tag, count=1)
hero_tag = re.sub(r'srcset="[^"]+"', f'srcset="{hero_srcset}"', hero_tag, count=1)
hero_tag = re.sub(r'width="\d+"\s+height="\d+"', f'width="{hero_source_width}" height="{hero_source_height}"', hero_tag, count=1)
if 'fetchpriority=' not in hero_tag:
    hero_tag = hero_tag[:-1] + ' fetchpriority="high">'
index = index[:hero_img.start()] + hero_tag + index[hero_img.end():]

# The editorial event image was previously sent as the 1335 px master even
# when rendered ~358 px wide. Generate real responsive candidates and attach
# them to every homepage use of that authentic image.
event_widths = (400, 640, 960, 1200)
event_source_width = event_source_height = None
for width in event_widths:
    sw, sh = write_variant('images/eventbild1.png', width, quality=78 if width <= 640 else 80)
    event_source_width, event_source_height = sw, sh
assert event_source_width and event_source_height
event_candidates = [f'images/eventbild1-{w}.webp {w}w' for w in event_widths if w < event_source_width]
event_candidates.append(f'images/eventbild1.webp {event_source_width}w')
event_srcset = ', '.join(event_candidates)

def responsive_event(match: re.Match) -> str:
    tag = match.group(0)
    tag = re.sub(r'src="images/eventbild1\.webp"', 'src="images/eventbild1-400.webp"', tag, count=1)
    if 'srcset=' in tag:
        tag = re.sub(r'srcset="[^"]+"', f'srcset="{event_srcset}"', tag, count=1)
    else:
        tag = tag[:-1] + f' srcset="{event_srcset}" sizes="(max-width:820px) calc(100vw - 32px), 50vw">'
    tag = re.sub(r'width="\d+"\s+height="\d+"', f'width="{event_source_width}" height="{event_source_height}"', tag, count=1)
    return tag

index, event_count = re.subn(
    r'<img\b(?=[^>]*\bsrc="images/eventbild1\.webp")[^>]*>',
    responsive_event,
    index,
)
assert event_count >= 2

# Add a 400 px lesson candidate so the prominent Unterricht image does not
# send 480 physical pixels to a ~358 CSS-pixel mobile slot.
lesson_source_width, lesson_source_height = write_variant('images/reistunde1.png', 400, quality=78)
lesson_img = re.search(r'<img\b(?=[^>]*\balt="Reitunterricht auf der Reitanlage Eichhorn-Nels")[^>]*>', index)
assert lesson_img
lesson_tag = lesson_img.group(0)
lesson_srcset_match = re.search(r'srcset="([^"]+)"', lesson_tag)
assert lesson_srcset_match
lesson_srcset = lesson_srcset_match.group(1)
if 'reistunde1-400.webp' not in lesson_srcset:
    lesson_srcset = 'images/reistunde1-400.webp 400w, ' + lesson_srcset
lesson_tag = re.sub(r'srcset="[^"]+"', f'srcset="{lesson_srcset}"', lesson_tag, count=1)
lesson_tag = re.sub(r'sizes="[^"]+"', 'sizes="(max-width:820px) calc(100vw - 32px), 82vw"', lesson_tag, count=1)
index = index[:lesson_img.start()] + lesson_tag + index[lesson_img.end():]

INDEX.write_text(index, encoding='utf-8')

# Contrast fixes are intentionally narrow. They retain the visual hierarchy but
# provide a safe margin above WCAG AA rather than sitting on the 4.5:1 boundary.
css = CSS.read_text(encoding='utf-8')
marker = '/* ===== release-quality-20260912 ===== */'
assert marker not in css
css += f'''\n\n{marker}
body:not(.journal-page) .chapter-light .chapter-index>.kicker{{color:#785a3f!important}}
body:not(.journal-page) .footer .wordmark span,
body:not(.journal-page) .footer>p,
body:not(.journal-page) .footer>p span{{color:#59635e!important}}
body:not(.journal-page) .price-highlight dd.price-note{{
  grid-column:1/-1!important;
  margin:0!important;
  color:rgba(248,245,239,.76)!important;
  font-family:var(--sans)!important;
  font-size:.69rem!important;
  font-weight:400!important;
  line-height:1.5!important;
  letter-spacing:0!important;
}}
'''
CSS.write_text(css, encoding='utf-8')

# Release assertions: fail here instead of shipping a partially transformed
# document if upstream markup changes later.
final_index = INDEX.read_text(encoding='utf-8')
assert 'class="wordmark" href="#start" aria-label=' not in final_index
assert '<dd class="price-note">3 × 30 Min. + Einführung</dd>' in final_index
assert '<script defer src="site.js?v=' in final_index
assert 'imagesrcset="images/reitbeteiligung1-400.webp 400w' in final_index
assert final_index.count('images/eventbild1-400.webp') >= 2
assert 'images/reistunde1-400.webp 400w' in final_index
print('Applied release accessibility and critical-path image delivery fixes.')
