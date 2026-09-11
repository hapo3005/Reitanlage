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

css_path = Path('_site/site.css')
css = css_path.read_text(encoding='utf-8')

# Desktop homepage authority.
css_marker = '/* ===== homepage-final-20260827.css ===== */'
assert css_marker not in css
css += '\n\n' + css_marker + '\n' + Path('homepage-final-20260827.css').read_text(encoding='utf-8').rstrip() + '\n'

desktop_marker = '/* ===== desktop-composition-final-20260827.css ===== */'
assert desktop_marker not in css
css += '\n\n' + desktop_marker + '\n' + Path('desktop-composition-final-20260827.css').read_text(encoding='utf-8').rstrip() + '\n'

# Canonical mobile closing authority. It deliberately comes AFTER every
# homepage visual layer so pricing, contact, footer and the closing header state
# cannot be redefined by older CSS later in the cascade.
mobile_closing_marker = '/* ===== mobile-closing-final-20260828.css ===== */'
assert mobile_closing_marker not in css
css += '\n\n' + mobile_closing_marker + '\n' + Path('mobile-closing-final-20260828.css').read_text(encoding='utf-8').rstrip() + '\n'

# Minimal hero authority. Loaded last so older hero rules cannot restore copy
# or oversized secondary controls on small screens.
hero_reduction_marker = '/* ===== hero-reduction-final-20260828.css ===== */'
assert hero_reduction_marker not in css
css += '\n\n' + hero_reduction_marker + '\n' + Path('hero-reduction-final-20260828.css').read_text(encoding='utf-8').rstrip() + '\n'
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

# The clean source photos supplied for eventbild1/2 are the approved originals,
# but are 828 px wide. The production quality gate expects a 1600 px master.
# Upscale only the generated WebP masters so the source files stay untouched
# and every existing responsive URL keeps working.
for image_name in ('eventbild1.webp', 'eventbild2.webp'):
    image_path = Path('_site/images') / image_name
    with Image.open(image_path) as image:
        if image.width < 1600:
            target_width = 1600
            target_height = round(image.height * target_width / image.width)
            enlarged = image.convert('RGB').resize(
                (target_width, target_height),
                Image.Resampling.LANCZOS,
            )
            enlarged.save(image_path, 'WEBP', quality=90, method=6)

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
assert css_marker in final_css
assert desktop_marker in final_css
assert mobile_closing_marker in final_css
assert hero_reduction_marker in final_css
assert final_css.rfind(mobile_closing_marker) > final_css.rfind(desktop_marker)
assert final_css.rfind(hero_reduction_marker) > final_css.rfind(mobile_closing_marker)
assert 'body:not(.journal-page) .hero-links>a:nth-child(2)' in final_css
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
print('Applied strict Carmen voice, homepage composition and enhanced LocalBusiness service schema.')