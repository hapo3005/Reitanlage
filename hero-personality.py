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

# A visible FAQ belongs immediately before contact: at this point visitors have
# already seen services, horses, current news and prices, so the section can
# remove the last practical uncertainties before they get in touch.
faq_marker = '<section class="contact contact-editorial" id="kontakt">'
assert 'class="faq-section"' not in html
assert faq_marker in html
faq = '''<section class="faq-section" id="fragen" aria-labelledby="faq-title">
  <div class="faq-intro" data-reveal>
    <p class="kicker">Gut zu wissen</p>
    <h2 id="faq-title">Was Sie vor dem ersten Besuch <em>wissen möchten.</em></h2>
    <p class="faq-lede">Die wichtigsten Fragen zu Unterricht, Lehrpferden, Pension und dem ersten Kontakt beantworte ich Ihnen hier direkt.</p>
    <a class="faq-contact-link" href="#kontakt">Frage nicht dabei? Direkt fragen <span aria-hidden="true">→</span></a>
  </div>
  <div class="faq-list">
    <details class="faq-item" data-reveal>
      <summary><span class="faq-number">01</span><span>Für wen ist der Reitunterricht geeignet?</span></summary>
      <div class="faq-answer"><p>Ich unterrichte Kinder, Jugendliche und Erwachsene – vom Anfänger und Wiedereinsteiger bis zum Freizeit- und Turnierreiter. Der Unterricht richtet sich nach dem jeweiligen Ausbildungsstand von Reiter und Pferd.</p></div>
    </details>
    <details class="faq-item" data-reveal>
      <summary><span class="faq-number">02</span><span>Brauche ich ein eigenes Pferd?</span></summary>
      <div class="faq-answer"><p>Nein. Sie können mit einem meiner Lehrpferde oder mit dem eigenen Pferd zum Unterricht kommen. Für Anfänger und Wiedereinsteiger stehen ausgebildete Lehrpferde zur Verfügung.</p></div>
    </details>
    <details class="faq-item" data-reveal>
      <summary><span class="faq-number">03</span><span>Welche Unterrichtsformen gibt es?</span></summary>
      <div class="faq-answer"><p>Je nach Ausbildungsstand sind Einzel- und Gruppenunterricht, Longenunterricht, Dressur, Cavaletti, Springgymnastik und Parcoursarbeit möglich. Auch gezielte Turniervorbereitung gehört zum Angebot.</p></div>
    </details>
    <details class="faq-item" data-reveal>
      <summary><span class="faq-number">04</span><span>Was kostet Reitunterricht?</span></summary>
      <div class="faq-answer"><p>Die aktuell gültigen Preise finden Sie direkt im <a href="#preise">Preisbereich</a> über diesen Fragen. Dort sind Unterricht, Karten, Pferdepension und Pferdeausbildung übersichtlich aufgeführt.</p></div>
    </details>
    <details class="faq-item" data-reveal>
      <summary><span class="faq-number">05</span><span>Gibt es Pferdepension auf der Anlage?</span></summary>
      <div class="faq-answer"><p>Ja. Zur Anlage gehören 18 helle Pony-, Großpferd- und Paddockboxen. Je nach Wetter kommen die Pferde täglich in kleinen Gruppen auf die Weide oder aufs Paddock; das Heu stammt aus eigenem Anbau.</p></div>
    </details>
    <details class="faq-item" data-reveal>
      <summary><span class="faq-number">06</span><span>Welche Trainingsmöglichkeiten gibt es vor Ort?</span></summary>
      <div class="faq-answer"><p>Reithalle und Außenplatz sind jeweils etwa 20 × 40 Meter groß. Außerdem gehören ein Waschplatz, ein Solarium und eine beheizte Sattelkammer zur Anlage. Direkt vom Hof führen Wege ins umliegende Gelände.</p></div>
    </details>
    <details class="faq-item" data-reveal>
      <summary><span class="faq-number">07</span><span>Werden auch Beritt und Turnierbetreuung angeboten?</span></summary>
      <div class="faq-answer"><p>Ja. Möglich sind Einzel-, Teil- und Vollberitt sowie Longieren und Bodenarbeit. Je nach Vereinbarung begleite ich Schüler, Einsteller und Privatreiter außerdem bei der Vorbereitung und auf Turnieren oder stelle Pferde selbst vor.</p></div>
    </details>
    <details class="faq-item" data-reveal>
      <summary><span class="faq-number">08</span><span>Gibt es Ferienreitkurse, Lehrgänge oder Reitabzeichen?</span></summary>
      <div class="faq-answer"><p>Diese Angebote gehören immer wieder zum Hofleben. Die Termine wechseln – wenn Sie wissen möchten, was aktuell geplant ist oder ob noch ein Platz frei ist, fragen Sie bitte direkt bei mir nach.</p></div>
    </details>
    <details class="faq-item" data-reveal>
      <summary><span class="faq-number">09</span><span>Muss ich einen Besuch vorher abstimmen?</span></summary>
      <div class="faq-answer"><p>Ja. Wenn Sie die Anlage kennenlernen oder etwas persönlich besprechen möchten, stimmen Sie den Termin bitte vorher kurz mit mir ab. Am einfachsten erreichen Sie mich per WhatsApp, Telefon oder E-Mail.</p></div>
    </details>
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
assert 'Was Sie vor dem ersten Besuch <em>wissen möchten.</em>' in html
path.write_text(html, encoding='utf-8')

# Editorial FAQ styling. Native details/summary keeps the interaction fast,
# keyboard-accessible and resilient without introducing another JS dependency.
css_path = Path('_site/site.css')
css = css_path.read_text(encoding='utf-8')
faq_css_marker = '/* ===== faq-premium-20260911 ===== */'
assert faq_css_marker not in css
faq_css = r'''
/* ===== faq-premium-20260911 ===== */
.faq-section{padding:clamp(76px,9vw,128px) max(30px,calc((100vw - 1280px)/2));background:#f1ece2;color:#173027;display:grid;grid-template-columns:minmax(260px,.72fr) minmax(0,1.28fr);gap:clamp(48px,7vw,112px);align-items:start;border-top:1px solid rgba(23,48,39,.08)}
.faq-intro{position:sticky;top:118px;max-width:470px}
.faq-intro .kicker{margin:0 0 20px;color:#9b7555;letter-spacing:.18em;text-transform:uppercase;font-size:.78rem;font-weight:700}
.faq-intro h2{margin:0;font-family:Georgia,"Times New Roman",serif;font-size:clamp(2.45rem,4.3vw,4.65rem);font-weight:400;line-height:.98;letter-spacing:-.04em;color:#173027}
.faq-intro h2 em{font-weight:400;color:#9b7555}
.faq-lede{max-width:38rem;margin:28px 0 0;font-size:1.03rem;line-height:1.72;color:rgba(23,48,39,.72)}
.faq-contact-link{display:inline-flex;align-items:center;gap:12px;margin-top:30px;color:#173027;text-decoration:none;font-weight:700;border-bottom:1px solid rgba(23,48,39,.32);padding-bottom:6px;transition:border-color .18s ease,gap .18s ease}
.faq-contact-link:hover{gap:16px;border-color:#9b7555}
.faq-contact-link:focus-visible,.faq-item summary:focus-visible{outline:3px solid rgba(155,117,85,.38);outline-offset:5px;border-radius:3px}
.faq-list{border-top:1px solid rgba(23,48,39,.18)}
.faq-item{border-bottom:1px solid rgba(23,48,39,.18)}
.faq-item summary{display:grid;grid-template-columns:42px minmax(0,1fr) 38px;gap:18px;align-items:center;min-height:82px;padding:18px 0;cursor:pointer;list-style:none;font-size:clamp(1.02rem,1.35vw,1.22rem);line-height:1.35;font-weight:650;color:#173027;transition:color .18s ease}
.faq-item summary::-webkit-details-marker{display:none}
.faq-item summary::marker{content:""}
.faq-number{font-size:.7rem;letter-spacing:.16em;color:#9b7555;font-weight:700}
.faq-item summary::after{content:"+";display:grid;place-items:center;width:34px;height:34px;border:1px solid rgba(23,48,39,.22);border-radius:50%;font:400 1.2rem/1 Georgia,"Times New Roman",serif;color:#173027;transition:background .18s ease,color .18s ease,border-color .18s ease,transform .18s ease}
.faq-item summary:hover{color:#9b7555}
.faq-item summary:hover::after{border-color:#9b7555;transform:translateY(-1px)}
.faq-item[open] summary::after{content:"−";background:#173027;border-color:#173027;color:#f4f0e7;transform:none}
.faq-answer{padding:0 54px 24px 60px;max-width:760px}
.faq-answer p{margin:0;font-size:.98rem;line-height:1.75;color:rgba(23,48,39,.74)}
.faq-answer a{color:#173027;text-decoration-thickness:1px;text-underline-offset:3px}
.faq-item[open] .faq-answer{animation:faqAnswerIn .22s ease both}
@keyframes faqAnswerIn{from{opacity:0;transform:translateY(-5px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:820px){
  .faq-section{display:block;padding:72px 30px 78px}
  .faq-intro{position:static;max-width:none;margin-bottom:34px}
  .faq-intro h2{font-size:clamp(2.3rem,10vw,3.25rem);line-height:1.02}
  .faq-lede{margin-top:22px;font-size:.98rem}
  .faq-contact-link{margin-top:24px}
  .faq-item summary{grid-template-columns:30px minmax(0,1fr) 34px;gap:12px;min-height:76px;padding:17px 0;font-size:1rem}
  .faq-number{font-size:.64rem}
  .faq-item summary::after{width:32px;height:32px}
  .faq-answer{padding:0 38px 22px 42px}
  .faq-answer p{font-size:.95rem;line-height:1.68}
}
@media(prefers-reduced-motion:reduce){.faq-contact-link,.faq-item summary,.faq-item summary::after{transition:none}.faq-item[open] .faq-answer{animation:none}}
'''.strip()
css_path.write_text(css.rstrip() + '\n\n' + faq_css + '\n', encoding='utf-8')

final_css = css_path.read_text(encoding='utf-8')
assert final_css.count(faq_css_marker) == 1
assert '.faq-item[open] summary::after' in final_css
assert '@media(max-width:820px)' in final_css
print('Applied minimal hero and premium visitor FAQ section.')
