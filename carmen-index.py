from pathlib import Path
import json
import os
import re

from PIL import Image

# Reuse the reviewed homepage copy map without executing the journal pass in
# carmen-voice.py. This keeps the homepage transformation strict and fails the
# build if its source copy changes unexpectedly.
source = Path('carmen-voice.py').read_text(encoding='utf-8')
prefix = source.split('\njournal_replacements =', 1)[0]
namespace = {}
exec(prefix, namespace)
namespace['replace_many'](Path('_site/index.html'), namespace['index_replacements'])

# Keep the opening intentionally minimal: identity, message and actions only.
exec(Path('hero-personality.py').read_text(encoding='utf-8'), {})

# One deterministic late homepage bundle. The source modules remain separated by
# responsibility, but production gets one ordered authority block plus one small
# premium finish layer. This prevents future ad-hoc append chains.
css_path = Path('_site/site.css')
css = css_path.read_text(encoding='utf-8')
homepage_modules = (
    'homepage-final-20260827.css',
    'desktop-composition-final-20260827.css',
    'mobile-closing-final-20260828.css',
    'hero-reduction-final-20260828.css',
)
authority_marker = '/* ===== homepage-authority-bundle ===== */'
premium_marker = '/* ===== homepage-premium-final.css ===== */'
assert authority_marker not in css
assert premium_marker not in css
module_chunks = []
for name in homepage_modules:
    module_text = Path(name).read_text(encoding='utf-8').rstrip()
    assert module_text
    module_chunks.append(f'/* module: {name} */\n{module_text}')
css += '\n\n' + authority_marker + '\n' + '\n\n'.join(module_chunks) + '\n'
premium_css = Path('homepage-premium-final.css').read_text(encoding='utf-8').rstrip()
assert 'dark chapters must always restore' not in Path('hero-reduction-final-20260828.css').read_text(encoding='utf-8')
css += '\n\n' + premium_marker + '\n' + premium_css + '\n'
css_path.write_text(css, encoding='utf-8')

# Deterministic contact-active state near the bottom of the page.
js_path = Path('_site/site.js')
js_marker = '/* ===== homepage-final-20260827.js ===== */'
js = js_path.read_text(encoding='utf-8')
assert js_marker not in js
js += '\n\n' + js_marker + '\n' + Path('homepage-final-20260827.js').read_text(encoding='utf-8').rstrip() + '\n'

# Mobile closing behavior is appended last for the homepage: once pricing is
# reached, the floating header leaves the viewport and no longer obscures the
# final price/contact composition.
mobile_closing_js_marker = '/* ===== mobile-closing-final-20260828.js ===== */'
assert mobile_closing_js_marker not in js
js += '\n\n' + mobile_closing_js_marker + '\n' + Path('mobile-closing-final-20260828.js').read_text(encoding='utf-8').rstrip() + '\n'
js_path.write_text(js, encoding='utf-8')

# Curate the strongest authentic lesson image into the large Unterricht visual.
# Unlike the former event-image upscale, this keeps source fidelity: no image is
# enlarged merely to satisfy a nominal pixel gate.
curated_source = Path('images/reistunde1.png')
curated_full = Path('_site/images/reistunde1.webp')
curated_variants = []
with Image.open(curated_source) as image:
    source_width, source_height = image.size
    rgb = image.convert('RGB')
    rgb.save(curated_full, 'WEBP', quality=88, method=6)
    for width in (480, 800, 1200):
        if width >= source_width:
            continue
        height = round(source_height * width / source_width)
        resized = rgb.resize((width, height), Image.Resampling.LANCZOS)
        variant = Path(f'_site/images/reistunde1-{width}.webp')
        resized.save(variant, 'WEBP', quality=85, method=6)
        curated_variants.append((width, variant.name))

# Structured data: make the business, website and actual service portfolio
# explicit without adding invisible claims that are not present on the page.
site_url = os.environ.get('SITE_URL', 'https://hapo3005.github.io/Reitanlage/').rstrip('/') + '/'
business_id = site_url + '#business'
website_id = site_url + '#website'
webpage_id = site_url + '#webpage'

services = [
    ('Reitunterricht', 'Reitunterricht für Kinder, Jugendliche und Erwachsene mit Schul- oder Privatpferd.', '#ausbildung'),
    ('Pferdepension', 'Pferdepension mit hellen Boxen, täglichem Auslauf und Heu aus eigenem Anbau.', '#anlage'),
    ('Beritt und Pferdeausbildung', 'Einzel-, Teil- und Vollberitt sowie Longieren und Bodenarbeit.', '#ausbildung'),
    ('Geführte Ausritte', 'Geführte Ausritte nach Absprache und mit entsprechender Reiterfahrung.', '#anlage'),
    ('Ferienreitkurse und Reitabzeichen', 'Ferienreitkurse, Lehrgänge und Vorbereitung auf Reitabzeichen nach aktuellem Angebot.', '#aktuelles'),
    ('Turnierbetreuung', 'Vorbereitung, Betreuung auf Turnieren und Vorstellung von Pferden nach Vereinbarung.', '#pferde'),
]

offers = []
for name, description, anchor in services:
    offers.append({
        '@type': 'Offer',
        'itemOffered': {
            '@type': 'Service',
            'name': name,
            'description': description,
            'url': site_url + anchor,
            'provider': {'@id': business_id},
        },
    })

schema = {
    '@context': 'https://schema.org',
    '@graph': [
        {
            '@type': 'WebSite',
            '@id': website_id,
            'url': site_url,
            'name': 'Reitanlage Eichhorn-Nels',
            'inLanguage': 'de-DE',
            'publisher': {'@id': business_id},
        },
        {
            '@type': ['SportsActivityLocation', 'LocalBusiness'],
            '@id': business_id,
            'name': 'Reitanlage Eichhorn-Nels',
            'url': site_url,
            'telephone': '+49 174 3156082',
            'email': 'eichhorn.c@t-online.de',
            'image': site_url + 'social-preview.jpg',
            'priceRange': '€€',
            'address': {
                '@type': 'PostalAddress',
                'streetAddress': 'Siedlung Dadscheid 3',
                'postalCode': '54518',
                'addressLocality': 'Minderlittgen',
                'addressRegion': 'Rheinland-Pfalz',
                'addressCountry': 'DE',
            },
            'sameAs': ['https://www.facebook.com/groups/403038393066632/'],
            'hasOfferCatalog': {
                '@type': 'OfferCatalog',
                'name': 'Leistungen der Reitanlage Eichhorn-Nels',
                'itemListElement': offers,
            },
        },
        {
            '@type': 'WebPage',
            '@id': webpage_id,
            'url': site_url,
            'name': 'Reitunterricht & Pferdepension bei Wittlich · Eichhorn-Nels',
            'description': 'Reitunterricht für Kinder, Jugendliche und Erwachsene in Minderlittgen bei Wittlich. Dazu Pferdepension, Beritt, Ausritte, Reitabzeichen und Turnierbetreuung.',
            'isPartOf': {'@id': website_id},
            'about': {'@id': business_id},
            'primaryImageOfPage': {
                '@type': 'ImageObject',
                'url': site_url + 'social-preview.jpg',
            },
            'inLanguage': 'de-DE',
        },
    ],
}

index_path = Path('_site/index.html')
index = index_path.read_text(encoding='utf-8')

# Replace only the large Unterricht image; the facility gallery keeps its own
# documented event photos. The curated image receives responsive sources.
source_candidates = [f'images/{name} {width}w' for width, name in curated_variants]
source_candidates.append(f'images/reistunde1.webp {source_width}w')
lesson_tag = (
    f'<img src="images/reistunde1.webp" '
    f'srcset="{", ".join(source_candidates)}" '
    f'sizes="(max-width:820px) 100vw, 82vw" '
    f'alt="Reitunterricht auf der Reitanlage Eichhorn-Nels" '
    f'width="{source_width}" height="{source_height}" decoding="async" loading="lazy">'
)
index, curated_count = re.subn(
    r'<img\b(?=[^>]*\balt="Reitsport auf der Reitanlage Eichhorn-Nels")[^>]*>',
    lesson_tag,
    index,
    count=1,
)
assert curated_count == 1

schema_script = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(',', ':')) + '</script>'
index, schema_count = re.subn(
    r'<script type="application/ld\+json">.*?</script>',
    schema_script,
    index,
    count=1,
    flags=re.S,
)
assert schema_count == 1
index_path.write_text(index, encoding='utf-8')

# Validate the generated graph before security-hardening adds its CSP hashes.
match = re.search(r'<script type="application/ld\+json">(.*?)</script>', index, re.S)
assert match
parsed_schema = json.loads(match.group(1))
graph = parsed_schema['@graph']
business = next(node for node in graph if business_id == node.get('@id'))
assert 'LocalBusiness' in business['@type']
assert business['hasOfferCatalog']['@type'] == 'OfferCatalog'
assert len(business['hasOfferCatalog']['itemListElement']) == len(services)
assert all(item['itemOffered']['@type'] == 'Service' for item in business['hasOfferCatalog']['itemListElement'])

final_css = css_path.read_text(encoding='utf-8')
final_js = js_path.read_text(encoding='utf-8')
assert 'Was Carmen im Unterricht' not in index
assert 'Schreiben Sie Carmen gern' not in index
assert 'Reiten beginnt für mich mit <em>Vertrauen.</em>' in index
assert 'Was mir beim Reiten <em>wichtig ist.</em>' in index
assert 'melden Sie sich <em>gern bei mir.</em>' in index
assert 'class="hero-signature"' not in index
assert 'class="hero-intro"' not in index
assert 'class="credential"' not in index
assert 'Schön, dass Sie da sind.' not in index
assert 'Reitunterricht für Kinder, Jugendliche und Erwachsene – vom Einstieg bis zur Turniervorbereitung.' not in index
assert 'Trainer C Leistungssport · Dressur bis M · Springen bis L' not in index
assert 'images/reistunde1.webp' in index
assert 'alt="Reitunterricht auf der Reitanlage Eichhorn-Nels"' in index
assert authority_marker in final_css
assert premium_marker in final_css
assert final_css.count(authority_marker) == 1
assert final_css.count(premium_marker) == 1
assert final_css.rfind(premium_marker) > final_css.rfind(authority_marker)
for name in homepage_modules:
    assert f'/* module: {name} */' in final_css
assert 'body:not(.journal-page) .hero-links>a:nth-child(2)' in final_css
assert 'body:not(.journal-page) .stable-copy>p:not(.kicker)' in final_css
assert 'color:rgba(248,245,239,.84)!important' in final_css
assert js_marker in final_js
assert mobile_closing_js_marker in final_js
assert final_js.rfind(mobile_closing_js_marker) > final_js.rfind(js_marker)
assert 'body.closing-zone:not(.nav-open) .header' in final_css
assert 'body:not(.journal-page) .contact.contact-editorial::after' in final_css
assert "body.classList.toggle('closing-zone', closing)" in final_js
assert ('height:560px!important' in final_css) or ('desktop-contact-v3' in final_css)
assert 'grid-template-columns:176px minmax(0,1fr)!important' in final_css
assert 'height:auto!important' in final_css
assert 'document.documentElement.scrollHeight-4' in final_js
print('Applied consolidated homepage authority, curated imagery and premium finish.')
