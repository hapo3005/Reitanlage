from pathlib import Path
import json
import os
import re

path = Path('_site/aktuelles.html')
text = path.read_text(encoding='utf-8')

required = (
    'Was bei uns auf dem Hof <em>passiert.</em>',
    'Hier nehme ich Sie ein bisschen ausführlicher mit in unseren Hofalltag',
    'Einblicke in unseren <em>Alltag.</em>',
    'Ein paar Rückblicke aus den <em>vergangenen Jahren.</em>',
    'Je nach Vereinbarung begleite ich Schüler, Einsteller und Privatreiter',
    'Termine und Verfügbarkeiten stimmen wir am besten direkt <em>ab.</em>',
)
for phrase in required:
    assert phrase in text, phrase

forbidden = (
    'Momente, die man nicht in eine <em>Preisliste</em> bekommt.',
    'Was bereits <em>passiert ist.</em>',
    'Carmen begleitet Schüler, Einsteller und Privatreiter',
    'Termine und Verfügbarkeiten am besten direkt <em>abstimmen.</em>',
)
for phrase in forbidden:
    assert phrase not in text, phrase

# Keep the primary navigation consistent across the homepage and Hofjournal.
nav_marker = '<a href="index.html#preise">Preise</a><a class="nav-cta" href="index.html#kontakt">Kontakt</a>'
assert nav_marker in text
assert 'href="index.html#fragen">Fragen</a>' not in text
text = text.replace(
    nav_marker,
    '<a href="index.html#preise">Preise</a><a href="index.html#fragen">Fragen</a><a class="nav-cta" href="index.html#kontakt">Kontakt</a>',
    1,
)

# Give each current Hofmeldung a stable fragment URL. This keeps the collection
# page compact while allowing structured data to identify every post uniquely.
news = json.loads(Path('_site/aktuelles.json').read_text(encoding='utf-8'))
items = [item for item in news.get('items', []) if item.get('title') and item.get('text')]
if items:
    text = text.replace(
        '<article class="journal-current-main">',
        '<article class="journal-current-main" id="meldung-1">',
        1,
    )
    for position in range(2, len(items) + 1):
        text = text.replace(
            '<article class="journal-current-side">',
            f'<article class="journal-current-side" id="meldung-{position}">',
            1,
        )

# Structured data: CollectionPage + breadcrumb + ItemList + BlogPosting entities
# for the actual current posts. No artificial FAQ markup or invented publish dates.
site_url = os.environ.get('SITE_URL', 'https://hapo3005.github.io/Reitanlage/').rstrip('/') + '/'
page_url = site_url + 'aktuelles.html'
business_id = site_url + '#business'
website_id = site_url + '#website'
page_id = page_url + '#webpage'
breadcrumb_id = page_url + '#breadcrumb'
list_id = page_url + '#current-posts'
updated = news.get('updated')

list_elements = []
blog_posts = []
for position, item in enumerate(items, start=1):
    post_id = page_url + f'#meldung-{position}'
    image = str(item.get('image', '')).strip()
    image_url = image if image.startswith(('https://', 'http://')) else site_url + image.lstrip('/')

    list_elements.append({
        '@type': 'ListItem',
        'position': position,
        'item': {'@id': post_id},
    })

    post = {
        '@type': 'BlogPosting',
        '@id': post_id,
        'url': post_id,
        'headline': item['title'],
        'description': item['text'],
        'image': image_url,
        'articleSection': item.get('category') or 'Aktuelles',
        'inLanguage': 'de-DE',
        'isAccessibleForFree': True,
        'author': {'@id': business_id},
        'publisher': {'@id': business_id},
        'mainEntityOfPage': {'@id': page_id},
        'isPartOf': {'@id': page_id},
    }
    if updated:
        post['dateModified'] = updated
    blog_posts.append(post)

collection = {
    '@type': 'CollectionPage',
    '@id': page_id,
    'url': page_url,
    'name': 'Aktuelles & Hofleben · Reitanlage Eichhorn-Nels',
    'description': 'Aktuelles, Ferienreitkurse, Hofleben, Turnierrückblicke und Bilder von der Reitanlage Eichhorn-Nels in Minderlittgen bei Wittlich.',
    'isPartOf': {'@id': website_id},
    'about': {'@id': business_id},
    'breadcrumb': {'@id': breadcrumb_id},
    'mainEntity': {'@id': list_id},
    'inLanguage': 'de-DE',
}
if updated:
    collection['dateModified'] = updated

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
            'address': {
                '@type': 'PostalAddress',
                'streetAddress': 'Siedlung Dadscheid 3',
                'postalCode': '54518',
                'addressLocality': 'Minderlittgen',
                'addressRegion': 'Rheinland-Pfalz',
                'addressCountry': 'DE',
            },
        },
        collection,
        {
            '@type': 'BreadcrumbList',
            '@id': breadcrumb_id,
            'itemListElement': [
                {
                    '@type': 'ListItem',
                    'position': 1,
                    'name': 'Startseite',
                    'item': site_url,
                },
                {
                    '@type': 'ListItem',
                    'position': 2,
                    'name': 'Aktuelles & Hofleben',
                    'item': page_url,
                },
            ],
        },
        {
            '@type': 'ItemList',
            '@id': list_id,
            'name': 'Aktuelle Meldungen der Reitanlage Eichhorn-Nels',
            'itemListOrder': 'https://schema.org/ItemListOrderDescending',
            'numberOfItems': len(items),
            'itemListElement': list_elements,
        },
        *blog_posts,
    ],
}

schema_script = '<script type="application/ld+json">' + json.dumps(schema, ensure_ascii=False, separators=(',', ':')) + '</script>'
text, schema_count = re.subn(
    r'<script type="application/ld\+json">.*?</script>',
    schema_script,
    text,
    count=1,
    flags=re.S,
)
assert schema_count == 1
path.write_text(text, encoding='utf-8')

# Validate the generated graph before the security pass hashes inline scripts.
match = re.search(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
assert match
parsed_schema = json.loads(match.group(1))
graph = parsed_schema['@graph']
assert any(node.get('@type') == 'BreadcrumbList' for node in graph)
item_list = next(node for node in graph if node.get('@type') == 'ItemList')
assert item_list['numberOfItems'] == len(items)
assert sum(node.get('@type') == 'BlogPosting' for node in graph) == len(items)
for position in range(1, len(items) + 1):
    assert f'id="meldung-{position}"' in text
assert text.count('href="index.html#fragen">Fragen</a>') == 1

# This script runs after the global final desktop/mobile layers in the deploy
# workflow. Append the dedicated Hofjournal authority here so no older generic
# rule can re-introduce the oversized headings, stray rules or dead space.
css_path = Path('_site/site.css')
journal_css_path = Path('journal-10of10-20260827.css')
marker = '/* ===== journal-10of10-20260827.css ===== */'
css = css_path.read_text(encoding='utf-8')
assert marker not in css
css += '\n\n' + marker + '\n' + journal_css_path.read_text(encoding='utf-8').rstrip() + '\n'
css_path.write_text(css, encoding='utf-8')

final_css = css_path.read_text(encoding='utf-8')
assert final_css.count(marker) == 1
assert final_css.rfind(marker) > final_css.rfind('/* ===== final-10of10-20260827.css ===== */')
assert '.journal-page .journal-photoessay .journal-section-head h2' in final_css
assert 'grid-template-columns:repeat(12,minmax(0,1fr))!important' in final_css

print('Verified Carmen voice, Hofjournal design, FAQ navigation and structured data for current posts.')