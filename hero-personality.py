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
assert faq_css_marker not in css
faq_css = r'''
/* ===== faq-premium-20260911 ===== */
.faq-section{position:relative;overflow:clip;padding:clamp(84px,9vw,138px) max(30px,calc((100vw - 1360px)/2));background:linear-gradient(135deg,#f7f3eb 0%,#f1eadf 54%,#eee5d8 100%);color:#173027;border-top:1px solid rgba(23,48,39,.08)}
.faq-section::before{content:"";position:absolute;inset:-20% auto auto -12%;width:46vw;height:46vw;min-width:440px;min-height:440px;border-radius:50%;background:radial-gradient(circle,rgba(179,145,103,.14) 0%,rgba(179,145,103,.045) 42%,transparent 70%);pointer-events:none}
.faq-shell{position:relative;z-index:1;display:grid;grid-template-columns:minmax(300px,.78fr) minmax(0,1.22fr);gap:clamp(54px,7vw,118px);align-items:start;max-width:1360px;margin:0 auto}
.faq-intro{position:sticky;top:120px;max-width:500px;padding-top:10px}
.faq-intro .kicker{margin:0 0 22px;color:#98714e;font-size:.75rem;font-weight:800;letter-spacing:.20em;text-transform:uppercase}
.faq-intro h2{max-width:9.6ch;margin:0;color:#173027;font-family:"Iowan Old Style","Palatino Linotype","Book Antiqua",Palatino,Georgia,serif;font-size:clamp(2.7rem,4.65vw,5.15rem);font-weight:500;line-height:.94;letter-spacing:-.052em}
.faq-intro h2 em{color:#98714e;font-weight:500}
.faq-lede{max-width:39rem;margin:30px 0 0;color:rgba(23,48,39,.72);font-size:1.04rem;line-height:1.75}
.faq-facts{display:flex;flex-wrap:wrap;gap:8px;margin:28px 0 0}
.faq-facts span{display:inline-flex;align-items:center;min-height:34px;padding:7px 11px;border:1px solid rgba(23,48,39,.14);border-radius:999px;background:rgba(255,255,255,.35);color:rgba(23,48,39,.72);font-size:.75rem;font-weight:700;letter-spacing:.015em;box-shadow:inset 0 1px 0 rgba(255,255,255,.55)}
.faq-contact-link{display:inline-flex;align-items:center;justify-content:space-between;gap:18px;min-height:52px;margin-top:34px;padding:7px 8px 7px 18px;border:1px solid #17382d;border-radius:999px;background:#17382d;color:#f4f0e7;text-decoration:none;font-size:.9rem;font-weight:750;box-shadow:0 12px 28px rgba(13,39,28,.13);transition:transform .18s ease,box-shadow .18s ease,background .18s ease}
.faq-contact-arrow{display:grid;place-items:center;width:36px;height:36px;border-radius:50%;background:#f4f0e7;color:#17382d;font:500 1.05rem/1 system-ui,sans-serif;transition:transform .18s ease}
.faq-contact-link:hover{transform:translateY(-2px);background:#1b4033;box-shadow:0 16px 34px rgba(13,39,28,.17)}
.faq-contact-link:hover .faq-contact-arrow{transform:translateX(2px)}
.faq-contact-link:focus-visible,.faq-item summary:focus-visible{outline:3px solid rgba(179,145,103,.56);outline-offset:4px}

.faq-panel{position:relative;overflow:hidden;border:1px solid rgba(244,240,231,.16);border-radius:30px;background:linear-gradient(150deg,#17382d 0%,#112b22 58%,#0f271f 100%);box-shadow:0 32px 80px rgba(10,30,21,.18),inset 0 1px 0 rgba(255,255,255,.08)}
.faq-panel::before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 86% 2%,rgba(179,145,103,.19),transparent 31%);pointer-events:none}
.faq-panel-head{position:relative;display:flex;align-items:center;justify-content:space-between;gap:20px;padding:23px 26px 19px;border-bottom:1px solid rgba(244,240,231,.14);color:rgba(244,240,231,.62);font-size:.69rem;font-weight:800;letter-spacing:.18em;text-transform:uppercase}
.faq-panel-head strong{color:#d3b08b;font-family:"Iowan Old Style","Palatino Linotype","Book Antiqua",Palatino,Georgia,serif;font-size:.96rem;font-style:italic;font-weight:500;line-height:1;letter-spacing:-.02em;text-transform:none;white-space:nowrap}
.faq-list{position:relative}
.faq-item{margin:0;border:0;border-bottom:1px solid rgba(244,240,231,.12);background:transparent;transition:background .2s ease}
.faq-item:last-child{border-bottom:0}
.faq-item summary{display:grid;grid-template-columns:minmax(0,1fr) 42px;gap:22px;align-items:center;min-height:88px;padding:22px 26px 22px 30px;cursor:pointer;list-style:none;color:#f4f0e7;font-family:"Iowan Old Style","Palatino Linotype","Book Antiqua",Palatino,Georgia,serif;font-size:clamp(1.08rem,1.32vw,1.28rem);font-weight:600;line-height:1.26;letter-spacing:-.018em;transition:color .18s ease,transform .18s ease}
.faq-item summary::-webkit-details-marker{display:none}
.faq-item summary::marker{content:""}
.faq-question{display:flex;align-items:flex-start;gap:14px;min-width:0}
.faq-question::before{content:"";flex:0 0 18px;width:18px;height:1px;margin-top:.72em;background:#d3b08b;opacity:.48;transition:width .2s ease,flex-basis .2s ease,opacity .2s ease}
.faq-item[open] .faq-question::before{flex-basis:28px;width:28px;opacity:.9}
.faq-item summary::after{content:"+";display:grid;place-items:center;width:38px;height:38px;border:1px solid rgba(244,240,231,.24);border-radius:50%;background:rgba(244,240,231,.035);color:#f4f0e7;font:300 1.28rem/1 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;transition:transform .24s cubic-bezier(.2,.8,.2,1),background .18s ease,border-color .18s ease,color .18s ease}
.faq-item summary:hover{color:#e1c4a3}
.faq-item summary:hover::after{border-color:rgba(211,176,139,.72);background:rgba(179,145,103,.10)}
.faq-item[open]{background:linear-gradient(90deg,rgba(255,255,255,.045),rgba(179,145,103,.055))}
.faq-item[open] summary{color:#f8f3ea}
.faq-item[open] summary::after{border-color:#d3b08b;background:#d3b08b;color:#17382d;transform:rotate(45deg)}
.faq-answer{max-width:780px;padding:0 68px 28px 62px}
.faq-answer p{margin:0;color:rgba(244,240,231,.72);font-size:.96rem;line-height:1.75}
.faq-answer a{color:#e1c4a3;text-decoration-color:rgba(225,196,163,.54);text-decoration-thickness:1px;text-underline-offset:3px}
.faq-item[open] .faq-answer{animation:faqAnswerIn .24s ease both}
@keyframes faqAnswerIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}

/* Eight primary destinations now have equal authority in the editorial nav rail. */
@media(min-width:821px){
  body .header nav.nav,body .header:not(.scrolled) nav.nav,body .header.scrolled nav.nav{grid-template-columns:repeat(8,minmax(0,1fr))!important;max-width:1240px!important;font-size:clamp(1.02rem,1.05vw,1.25rem)!important}
  body .header .wordmark,body .header:not(.scrolled) .wordmark,body .header.scrolled .wordmark{flex-basis:clamp(225px,16.5vw,292px)!important}
  body .header.scrolled nav.nav{max-width:1200px!important;font-size:clamp(.98rem,1vw,1.18rem)!important}
}
@media(min-width:821px) and (max-width:1180px){
  body .header nav.nav,body .header:not(.scrolled) nav.nav,body .header.scrolled nav.nav{font-size:clamp(.80rem,1.08vw,.94rem)!important}
  body .header .wordmark,body .header:not(.scrolled) .wordmark,body .header.scrolled .wordmark{flex-basis:clamp(172px,18vw,205px)!important;padding-right:14px!important}
  body .header nav.nav a,body .header nav.nav .nav-cta{padding-left:4px!important;padding-right:4px!important}
}

@media(max-width:820px){
  .faq-section{padding:74px max(18px,var(--m-gutter,18px)) 82px}
  .faq-section::before{width:110vw;height:110vw;min-width:0;min-height:0;top:-18%;left:-46%}
  .faq-shell{display:block}
  .faq-intro{position:static;max-width:none;padding:0;margin:0 0 36px}
  .faq-intro .kicker{margin-bottom:17px;font-size:.68rem}
  .faq-intro h2{max-width:10.5ch;font-size:clamp(2.35rem,10.6vw,3.55rem);line-height:.98}
  .faq-lede{max-width:34rem;margin-top:22px;font-size:.97rem;line-height:1.68}
  .faq-facts{margin-top:22px;gap:7px}
  .faq-facts span{min-height:32px;padding:6px 10px;font-size:.69rem}
  .faq-contact-link{width:100%;box-sizing:border-box;margin-top:26px;min-height:50px;font-size:.84rem}
  .faq-panel{border-radius:24px}
  .faq-panel-head{padding:18px 17px 15px;font-size:.61rem;letter-spacing:.14em}
  .faq-panel-head strong{font-size:.84rem}
  .faq-item summary{grid-template-columns:minmax(0,1fr) 34px;gap:13px;min-height:76px;padding:19px 17px 19px 18px;font-size:1rem;line-height:1.3}
  .faq-question{gap:11px}
  .faq-question::before{flex-basis:15px;width:15px}
  .faq-item[open] .faq-question::before{flex-basis:22px;width:22px}
  .faq-item summary::after{width:32px;height:32px;font-size:1.12rem}
  .faq-answer{padding:0 48px 24px 44px}
  .faq-answer p{font-size:.92rem;line-height:1.66}
}
@media(max-width:430px){
  .faq-section{padding-top:66px;padding-bottom:72px}
  .faq-intro h2{font-size:clamp(2.2rem,11.2vw,3.05rem)}
  .faq-contact-link{padding-left:15px}
  .faq-contact-arrow{width:34px;height:34px}
  .faq-panel{border-radius:21px}
  .faq-panel-head{align-items:flex-end}
  .faq-panel-head strong{max-width:8.5rem;text-align:right;line-height:1.08}
  .faq-item summary{grid-template-columns:minmax(0,1fr) 31px;gap:11px;padding:18px 15px;font-size:.96rem}
  .faq-answer{padding:0 42px 22px 41px}
}
@media(prefers-reduced-motion:reduce){.faq-contact-link,.faq-contact-arrow,.faq-item,.faq-item summary,.faq-item summary::after,.faq-question::before{transition:none}.faq-item[open] .faq-answer{animation:none}}
'''.strip()
css_path.write_text(css.rstrip() + '\n\n' + faq_css + '\n', encoding='utf-8')

final_css = css_path.read_text(encoding='utf-8')
assert final_css.count(faq_css_marker) == 1
assert 'grid-template-columns:repeat(8,minmax(0,1fr))!important' in final_css
assert '.faq-panel' in final_css
assert '.faq-item[open] summary::after' in final_css
print('Applied minimal hero, first-class FAQ navigation and premium FAQ chapter.')
