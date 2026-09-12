from pathlib import Path

path = Path('_site/index.html')
html = path.read_text(encoding='utf-8')

replacements = [
    (
        '<p class="kicker">Carmen Eichhorn-Nels · Reitanlage bei Wittlich</p>',
        '<p class="kicker">Reitanlage Eichhorn-Nels · Minderlittgen</p>'
    ),
    (
        '<h1>Reiten beginnt für mich mit <em>Vertrauen.</em></h1><p class="hero-intro">Schön, dass Sie da sind. Auf meiner Reitanlage in Minderlittgen begleite ich Kinder, Jugendliche und Erwachsene – vom ersten Reiten über den Wiedereinstieg bis zur Turniervorbereitung. Sie können mit einem meiner Lehrpferde oder mit dem eigenen Pferd zu mir kommen. Auch Beritt und Pferdepension gehören zu meinem Angebot.</p>',
        '<h1>Reiten beginnt für mich mit <em>Vertrauen.</em></h1>'
    ),
    (
        '<p class="credential">Carmen Eichhorn-Nels · Trainer C Leistungssport · Dressur bis M · Springen bis L</p>',
        ''
    ),
    (
        '>Per WhatsApp schreiben</a>',
        '>Direkt per WhatsApp anfragen</a>'
    ),
]

missing = []
for old, new in replacements:
    if old not in html:
        missing.append(old[:120])
    else:
        html = html.replace(old, new, 1)

if missing:
    raise RuntimeError('Hero source changed unexpectedly:\n- ' + '\n- '.join(missing))

# FAQ is a first-class homepage chapter and therefore belongs in the primary nav.
nav_marker = '<a href="#preise">Preise</a><a class="nav-cta" href="#kontakt">Kontakt</a>'
assert nav_marker in html
assert 'href="#fragen">Fragen</a>' not in html
html = html.replace(
    nav_marker,
    '<a href="#preise">Preise</a><a href="#fragen">Fragen</a><a class="nav-cta" href="#kontakt">Kontakt</a>',
    1,
)

# The FAQ sits directly before contact, but now reads as its own designed chapter
# rather than a utility block appended to the bottom of the page.
faq_marker = '<section class="contact contact-editorial" id="kontakt">'
assert 'class="faq-section"' not in html
assert faq_marker in html
faq = '''<section class="faq-section" id="fragen" aria-labelledby="faq-title">
  <div class="faq-shell">
    <div class="faq-intro" data-reveal>
      <p class="kicker">Fragen &amp; Antworten</p>
      <h2 id="faq-title">Was Sie vor dem ersten Besuch <em>wissen möchten.</em></h2>
      <p class="faq-lede">Die wichtigsten Fragen zu Unterricht, Lehrpferden, Pension und dem ersten Kontakt beantworte ich Ihnen hier direkt.</p>
      <div class="faq-facts" aria-label="Kurz zusammengefasst">
        <span>Schulpferd oder eigenes Pferd</span>
        <span>Kinder, Jugendliche &amp; Erwachsene</span>
        <span>Besuch bitte vorher abstimmen</span>
      </div>
      <a class="faq-contact-link" href="#kontakt"><span>Noch etwas offen? Carmen direkt fragen</span><span class="faq-contact-arrow" aria-hidden="true">→</span></a>
    </div>

    <div class="faq-panel" data-reveal>
      <div class="faq-panel-head"><span>Kurz &amp; persönlich beantwortet</span><strong>Carmen antwortet</strong></div>
      <div class="faq-list">
        <details class="faq-item">
          <summary><span class="faq-question">Für wen ist der Reitunterricht geeignet?</span></summary>
          <div class="faq-answer"><p>Ich unterrichte Kinder, Jugendliche und Erwachsene – vom Anfänger und Wiedereinsteiger bis zum Freizeit- und Turnierreiter. Der Unterricht richtet sich nach dem jeweiligen Ausbildungsstand von Reiter und Pferd.</p></div>
        </details>
        <details class="faq-item">
          <summary><span class="faq-question">Brauche ich ein eigenes Pferd?</span></summary>
          <div class="faq-answer"><p>Nein. Sie können mit einem meiner Lehrpferde oder mit dem eigenen Pferd zum Unterricht kommen. Für Anfänger und Wiedereinsteiger stehen ausgebildete Lehrpferde zur Verfügung.</p></div>
        </details>
        <details class="faq-item">
          <summary><span class="faq-question">Welche Unterrichtsformen gibt es?</span></summary>
          <div class="faq-answer"><p>Je nach Ausbildungsstand sind Einzel- und Gruppenunterricht, Longenunterricht, Dressur, Cavaletti, Springgymnastik und Parcoursarbeit möglich. Auch gezielte Turniervorbereitung gehört zum Angebot.</p></div>
        </details>
        <details class="faq-item">
          <summary><span class="faq-question">Was kostet Reitunterricht?</span></summary>
          <div class="faq-answer"><p>Die aktuell gültigen Preise finden Sie direkt im <a href="#preise">Preisbereich</a> über diesen Fragen. Dort sind Unterricht, Karten, Pferdepension und Pferdeausbildung übersichtlich aufgeführt.</p></div>
        </details>
        <details class="faq-item">
          <summary><span class="faq-question">Gibt es Pferdepension auf der Anlage?</span></summary>
          <div class="faq-answer"><p>Ja. Zur Anlage gehören 18 helle Pony-, Großpferd- und Paddockboxen. Je nach Wetter kommen die Pferde täglich in kleinen Gruppen auf die Weide oder aufs Paddock; das Heu stammt aus eigenem Anbau.</p></div>
        </details>
        <details class="faq-item">
          <summary><span class="faq-question">Welche Trainingsmöglichkeiten gibt es vor Ort?</span></summary>
          <div class="faq-answer"><p>Reithalle und Außenplatz sind jeweils etwa 20 × 40 Meter groß. Außerdem gehören ein Waschplatz, ein Solarium und eine beheizte Sattelkammer zur Anlage. Direkt vom Hof führen Wege ins umliegende Gelände.</p></div>
        </details>
        <details class="faq-item">
          <summary><span class="faq-question">Werden auch Beritt und Turnierbetreuung angeboten?</span></summary>
          <div class="faq-answer"><p>Ja. Möglich sind Einzel-, Teil- und Vollberitt sowie Longieren und Bodenarbeit. Je nach Vereinbarung begleite ich Schüler, Einsteller und Privatreiter außerdem bei der Vorbereitung und auf Turnieren oder stelle Pferde selbst vor.</p></div>
        </details>
        <details class="faq-item">
          <summary><span class="faq-question">Gibt es Ferienreitkurse, Lehrgänge oder Reitabzeichen?</span></summary>
          <div class="faq-answer"><p>Diese Angebote gehören immer wieder zum Hofleben. Die Termine wechseln – wenn Sie wissen möchten, was aktuell geplant ist oder ob noch ein Platz frei ist, fragen Sie bitte direkt bei mir nach.</p></div>
        </details>
        <details class="faq-item">
          <summary><span class="faq-question">Muss ich einen Besuch vorher abstimmen?</span></summary>
          <div class="faq-answer"><p>Ja. Wenn Sie die Anlage kennenlernen oder etwas persönlich besprechen möchten, stimmen Sie den Termin bitte vorher kurz mit mir ab. Am einfachsten erreichen Sie mich per WhatsApp, Telefon oder E-Mail.</p></div>
        </details>
      </div>
    </div>
  </div>
</section>'''
html = html.replace(faq_marker, faq + faq_marker, 1)

assert 'class="hero-signature"' not in html
assert 'class="hero-intro"' not in html
assert 'class="credential"' not in html
assert 'Schön, dass Sie da sind.' not in html
assert 'Reitunterricht für Kinder, Jugendliche und Erwachsene – vom Einstieg bis zur Turniervorbereitung.' not in html
assert 'Trainer C Leistungssport · Dressur bis M · Springen bis L' not in html
assert 'Reitanlage Eichhorn-Nels · Minderlittgen' in html
assert 'Direkt per WhatsApp anfragen' in html
assert 'Per WhatsApp schreiben' not in html
assert html.count('class="faq-section"') == 1
assert html.count('class="faq-item"') == 9
assert html.count('href="#fragen">Fragen</a>') == 1
assert 'Was Sie vor dem ersten Besuch <em>wissen möchten.</em>' in html
path.write_text(html, encoding='utf-8')

# Premium editorial FAQ: a light chapter with a deep-green answer panel creates
# a deliberate visual pause between pricing and contact while retaining the
# established forest / cream / bronze brand language.
css_path = Path('_site/site.css')
css = css_path.read_text(encoding='utf-8')
faq_css_marker = '/* ===== faq-premium-20260911 ===== */'
assert css.count(faq_css_marker) == 1
final_css = css_path.read_text(encoding='utf-8')
assert final_css.count(faq_css_marker) == 1
assert 'grid-template-columns:repeat(8,minmax(0,1fr))!important' in final_css
assert '.faq-panel' in final_css
assert '.faq-item[open] summary::after' in final_css
print('Applied minimal hero, first-class FAQ navigation and premium FAQ chapter.')
