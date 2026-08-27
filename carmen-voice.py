from pathlib import Path

OUT = Path('_site')


def replace_many(path: Path, replacements: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding='utf-8')
    missing = []
    for old, new in replacements:
        if old not in text:
            missing.append(old)
            continue
        text = text.replace(old, new)
    if missing:
        preview = '\n'.join(f'- {item[:120]}' for item in missing)
        raise RuntimeError(f'Editorial source text changed unexpectedly in {path}:\n{preview}')
    path.write_text(text, encoding='utf-8')


index_replacements = [
    ('>Über uns</a>', '>Meine Haltung</a>'),
    ('>Pferde</a>', '>Lehrpferde</a>'),
    ('<p class="kicker">Reitanlage Eichhorn-Nels · bei Wittlich</p><h1>Reitunterricht in <em>Minderlittgen.</em></h1><p class="hero-intro">Für Kinder, Jugendliche und Erwachsene – vom ersten Reiten über den Wiedereinstieg bis zur Turniervorbereitung. Persönlich begleitet von Carmen Eichhorn-Nels, mit Schulpferd oder eigenem Pferd. Auch Pferdepension und Beritt gehören zum Angebot.</p>',
     '<p class="kicker">Carmen Eichhorn-Nels · Reitanlage bei Wittlich</p><h1>Reiten beginnt für mich mit <em>Vertrauen.</em></h1><p class="hero-intro">Schön, dass Sie da sind. Auf meiner Reitanlage in Minderlittgen begleite ich Kinder, Jugendliche und Erwachsene – vom ersten Reiten über den Wiedereinstieg bis zur Turniervorbereitung. Sie können mit einem meiner Lehrpferde oder mit dem eigenen Pferd zu mir kommen. Auch Beritt und Pferdepension gehören zu meinem Angebot.</p>'),
    ('<h2>Was Carmen im Unterricht <em>wichtig ist.</em></h2><p class="lead">Ein korrekter Sitz, verständliche Hilfen und ein fairer Umgang mit dem Pferd bilden die Grundlage.</p><div class="copy-columns"><p>Carmen ist selbst im Turniersport aktiv und bildet sich regelmäßig in Dressur und Springen fort. Im Unterricht geht es nicht darum, möglichst schnell etwas „hinzubekommen“, sondern darum, Reiter und Pferd Schritt für Schritt weiterzubringen.</p><p>Willkommen sind Freizeitreiter genauso wie ambitionierte Turnierreiter. Anfänger und Wiedereinsteiger bekommen eine ruhige Grundlage, Fortgeschrittene können gezielt an den nächsten Ausbildungsschritten arbeiten.</p></div>',
     '<h2>Was mir beim Reiten <em>wichtig ist.</em></h2><p class="lead">Ich möchte, dass Reiter verstehen, was sie tun – und dass das Pferd dabei fair und verständlich behandelt wird.</p><div class="copy-columns"><p>Ich bin selbst im Turniersport aktiv und bilde mich regelmäßig in Dressur und Springen fort. Im Unterricht geht es mir nicht darum, möglichst schnell etwas „hinzubekommen“. Mir ist wichtiger, Reiter und Pferd Schritt für Schritt weiterzubringen und eine gute, verlässliche Grundlage zu schaffen.</p><p>Bei mir sind Freizeitreiter genauso willkommen wie ambitionierte Turnierreiter. Anfänger und Wiedereinsteiger dürfen in Ruhe ankommen, Fortgeschrittene können gezielt an den nächsten Ausbildungsschritten arbeiten.</p></div>'),
    ('<p class="kicker">Ausbildung & Unterricht</p><h2>Reitunterricht für Kinder, Jugendliche und <em>Erwachsene.</em></h2><p>Anfänger, Fortgeschrittene, Wiedereinsteiger sowie Freizeit- und Turnierreiter sind herzlich willkommen – mit Schulpferd oder eigenem Pferd.</p>',
     '<p class="kicker">Ausbildung & Unterricht</p><h2>Ich hole Sie dort ab, <em>wo Sie stehen.</em></h2><p>Ob Sie gerade anfangen, nach einer Pause wieder einsteigen oder schon länger reiten: Wir schauen gemeinsam, was für Sie und Ihr Pferd sinnvoll ist. Unterricht ist mit Lehrpferd oder eigenem Pferd möglich.</p>'),
    ('<h3>Dressur</h3><p>Einzel- und Gruppenunterricht mit Schul- oder Privatpferd. Je nach Ausbildungsstand geht es um Sitz, Hilfengebung, Losgelassenheit und die weitere dressurmäßige Arbeit.</p>',
     '<h3>Dressur</h3><p>Im Dressurunterricht arbeite ich mit Ihnen an Sitz, Hilfengebung, Losgelassenheit und einer sauberen, verständlichen Kommunikation mit dem Pferd. Einzel- und Gruppenunterricht sind mit Lehr- oder Privatpferd möglich.</p>'),
    ('<h3>Springen & Cavaletti</h3><p>Cavaletti, Springgymnastik und Parcoursarbeit werden passend zum jeweiligen Pferd und Reiter aufgebaut. Unterricht ist bis Klasse L möglich.</p>',
     '<h3>Springen & Cavaletti</h3><p>Cavaletti, Springgymnastik und Parcoursarbeit baue ich so auf, dass sie zum Ausbildungsstand von Reiter und Pferd passen. Dabei geht es nicht nur um Höhe, sondern vor allem um Rhythmus, Sicherheit und gutes Reiten. Unterricht ist bis Klasse L möglich.</p>'),
    ('<h3>Einstieg & Lehrpferde</h3><p>Wer neu anfängt oder nach einer Pause wieder einsteigen möchte, kann auf den ausgebildeten Lehrpferden in Ruhe beginnen. Dazu gehören Longenunterricht und Angebote für die jüngeren Reiter.</p>',
     '<h3>Einstieg & Lehrpferde</h3><p>Wenn Sie neu anfangen oder nach längerer Pause wieder einsteigen möchten, können Sie auf meinen Lehrpferden in Ruhe beginnen. Auch Longenunterricht und Angebote für jüngere Reiter gehören dazu.</p>'),
    ('<h3>Beritt & Turnier</h3><p>Auch die Ausbildung von Pferden gehört zum Angebot: Einzel-, Teil- und Vollberitt, Longieren und Bodenarbeit sowie Turnierbetreuung und die Vorstellung von Pferden.</p>',
     '<h3>Beritt & Turnier</h3><p>Auch bei der Ausbildung Ihres Pferdes kann ich Sie unterstützen – vom einzelnen Beritt über Teil- und Vollberitt bis zu Longieren und Bodenarbeit. Auf Wunsch begleite ich Sie außerdem bei der Turniervorbereitung oder stelle Pferde selbst vor.</p>'),
    ('<div class="service-ribbon" data-reveal><p><strong>Außerdem möglich</strong> Ausritte · Reitabzeichen & Lehrgänge · Ferienreitkurse · Voltigierabteilung „Yakari“ · Pferdesuche & Beratung · Foto-/Videoservice · Tage der offenen Stalltür mit Vorführungen · Beratung zur pferdegerechten Haltung</p></div>',
     '<div class="service-ribbon" data-reveal><p><strong>Darüber hinaus biete ich an</strong> Ausritte · Reitabzeichen & Lehrgänge · Ferienreitkurse · Voltigierabteilung „Yakari“ · Pferdesuche & Beratung · Foto-/Videoservice · Tage der offenen Stalltür mit Vorführungen · Beratung zur pferdegerechten Haltung</p></div>'),
    ('<h2>So leben und trainieren die Pferde <em>bei uns.</em></h2><p class="lead light-text">Helle Boxen, täglicher Auslauf, eigenes Heu und viel Platz auf rund 12 Hektar Weideland.</p><p>Zur Anlage gehören 18 helle Pony-, Großpferd- und Paddockboxen, sieben Winterpaddocks und ein allwettertaugliches Paddock. Reithalle und Außenplatz sind jeweils etwa 20 × 40 Meter groß.</p><p>Außerdem gibt es einen Waschplatz, ein Solarium und eine beheizte Sattelkammer. Das Heu stammt aus eigenem Anbau. Je nach Wetter kommen die Pferde täglich in kleinen Gruppen auf die Weide oder aufs Paddock.</p>',
     '<h2>Mir ist wichtig, dass die Pferde <em>gut leben.</em></h2><p class="lead light-text">Viel Bewegung, verlässliche Abläufe und eine Haltung, die zum Pferd passt, gehören für mich selbstverständlich dazu.</p><p>Auf der Anlage stehen 18 helle Pony-, Großpferd- und Paddockboxen zur Verfügung. Dazu kommen sieben Winterpaddocks, ein allwettertaugliches Paddock und rund 12 Hektar Weideland. Reithalle und Außenplatz sind jeweils etwa 20 × 40 Meter groß.</p><p>Je nach Wetter kommen die Pferde täglich in kleinen Gruppen auf die Weide oder aufs Paddock. Unser Heu stammt aus eigenem Anbau. Für die tägliche Arbeit gibt es außerdem einen Waschplatz, ein Solarium und eine beheizte Sattelkammer.</p>'),
    ('<h3>Vom Hof direkt ins Gelände.</h3><p>Die Wege führen direkt in die Wälder von Wittlich und Hupperath/Bergweiler. Auch Touren Richtung Karl, Kloster Himmerod, Manderscheid und Bettenfeld sind möglich. Geführte Ausritte können nach Absprache und mit entsprechender Reiterfahrung vereinbart werden; die Dauer liegt je nach Tour bei etwa ein bis drei Stunden.</p>',
     '<h3>Vom Hof direkt ins Gelände.</h3><p>Direkt ab der Anlage führen schöne Wege in die Wälder von Wittlich und Hupperath/Bergweiler. Je nach Tour geht es auch Richtung Karl, Kloster Himmerod, Manderscheid oder Bettenfeld. Geführte Ausritte vereinbare ich gern nach Absprache und bei entsprechender Reiterfahrung; je nach Strecke sind wir etwa ein bis drei Stunden unterwegs.</p>'),
    ('<p class="kicker">Unsere Lehrpferde</p><h2>Die Pferde, auf denen bei uns <em>gelernt wird.</em></h2><p>Alle Lehrpferde werden regelmäßig Korrektur geritten und kommen Sommer wie Winter täglich auf die Koppel.</p>',
     '<p class="kicker">Meine Lehrpferde</p><h2>Pferde, auf die ich mich im Unterricht <em>verlassen kann.</em></h2><p>Ich achte darauf, dass meine Lehrpferde regelmäßig Korrektur geritten werden. Sommer wie Winter kommen sie täglich auf die Koppel.</p>'),
    ('<p class="horse-note" data-reveal>Je nach Trainingsstand ist auch eine Turnierteilnahme mit Lehrpferden möglich – von der Jugendreiterprüfung bis zu A-Springen und Dressur.</p>',
     '<p class="horse-note" data-reveal>Wenn Ausbildungsstand und Kombination passen, ist mit meinen Lehrpferden auch eine Turnierteilnahme möglich – von der Jugendreiterprüfung bis zu A-Springen und Dressur.</p>'),
    ('<h2>Gemeinsam auf <em>Turnieren unterwegs.</em></h2><p>Carmen begleitet Schüler, Einsteller und Privatreiter regelmäßig auf Turniere. Je nach Vereinbarung hilft sie bei der Vorbereitung, betreut vor Ort oder stellt Pferde selbst vor.</p>',
     '<h2>Wenn Sie mehr möchten, begleite ich Sie auch <em>auf Turniere.</em></h2><p>Ich begleite Schüler, Einsteller und Privatreiter regelmäßig auf Turniere. Je nach Vereinbarung unterstütze ich bei der Vorbereitung, betreue vor Ort oder stelle Pferde selbst vor.</p>'),
    ('<h2>Neuigkeiten und <em>Termine.</em></h2></div><p>Hier gibt es aktuelle Hinweise zu Kursen, Reitbeteiligungen, Terminen und Neuigkeiten von der Anlage.</p>',
     '<h2>Was bei uns gerade <em>los ist.</em></h2></div><p>Hier halte ich Sie über Kurse, Reitbeteiligungen, Termine und Neuigkeiten von der Anlage auf dem Laufenden.</p>'),
    ('<article><span>PM-Mobil · 2023</span><p>2023 wurde die Reitanlage als einer von acht Betrieben und Vereinen in Rheinland-Pfalz vom PM-Mobil besucht.</p></article>',
     '<article><span>PM-Mobil · 2023</span><p>2023 war unsere Reitanlage einer von acht Betrieben und Vereinen in Rheinland-Pfalz, die vom PM-Mobil besucht wurden.</p></article>'),
    ('<article><span>Ferienkurse</span><p>Vom 25. bis 28. März 2024 fand ein Ferienreitkurs von 10 bis 16 Uhr statt. Neue Termine bitte direkt erfragen.</p></article>',
     '<article><span>Ferienkurse</span><p>Ferienreitkurse finden immer wieder statt. Wenn Sie einen aktuellen Termin suchen, fragen Sie mich bitte direkt – dann kann ich Ihnen sagen, was gerade geplant ist.</p></article>'),
    ('<article><span>Reitbeteiligungen</span><p>Reitbeteiligungen werden je nach Pferd individuell vereinbart. Kosten und Umfang besprechen wir persönlich.</p></article>',
     '<article><span>Reitbeteiligungen</span><p>Reitbeteiligungen vereinbare ich immer passend zum jeweiligen Pferd und zur Situation. Alles Weitere besprechen wir am besten persönlich.</p></article>'),
    ('<h2>Was Unterricht, Pension und <em>Beritt kosten.</em></h2><p>Die wichtigsten Preise stehen hier direkt im Überblick. Die vollständige Preisliste lässt sich darunter aufklappen.</p>',
     '<h2>Was Unterricht, Pension und <em>Beritt kosten.</em></h2><p>Mir ist wichtig, dass Sie vorab wissen, womit Sie rechnen können. Deshalb finden Sie hier die wichtigsten Preise direkt im Überblick; die vollständige Preisliste können Sie darunter aufklappen.</p>'),
    ('<h2>Noch Fragen? Melden Sie sich <em>gern.</em></h2><p>Ob Reitunterricht, Wiedereinstieg, Beritt oder ein Platz für Ihr Pferd: Schreiben Sie Carmen gern per WhatsApp oder rufen Sie an. Besuche auf der Anlage bitte vorher kurz abstimmen.</p>',
     '<h2>Wenn Sie Fragen haben, melden Sie sich <em>gern bei mir.</em></h2><p>Ob es um Reitunterricht, Wiedereinstieg, Beritt oder einen Platz für Ihr Pferd geht: Schreiben Sie mir gern per WhatsApp oder rufen Sie mich an. Wenn Sie die Anlage besuchen möchten, stimmen Sie den Termin bitte vorher kurz mit mir ab.</p>'),
]

journal_replacements = [
    ('<h1>Was auf dem Hof passiert.</h1>', '<h1>Was bei uns auf dem Hof passiert.</h1>'),
    ('<p>Aktuelle Hinweise, Ferienkurse, besondere Tage und Erinnerungen aus dem Stallalltag. Hier darf es ausführlicher werden als auf der Startseite – mit mehr Bildern, mehr Rückblicken und mehr von dem, was die Reitanlage ausmacht.</p>',
     '<p>Hier nehme ich Sie ein bisschen ausführlicher mit in unseren Hofalltag: mit aktuellen Hinweisen, Ferienkursen, besonderen Tagen und Erinnerungen aus den vergangenen Jahren.</p>'),
    ('<p>Die wichtigsten Hinweise stehen weiterhin kompakt auf der Startseite. Hier bekommen sie mehr Raum und werden später durch neue Meldungen und Rückblicke ergänzt.</p>',
     '<p>Die wichtigsten Hinweise finden Sie weiterhin kompakt auf der Startseite. Hier gibt es etwas mehr Platz für Neuigkeiten, Bilder und Rückblicke.</p>'),
    ('<h2>Mehr als nur eine Reitstunde.</h2><p>Ferienreitkurse gehören seit Jahren zum Angebot. Es wird geritten, geputzt, erklärt und natürlich viel Zeit mit den Pferden verbracht. Ein dokumentierter Kurs fand vom 25. bis 28. März 2024 jeweils von 10 bis 16 Uhr statt. Neue Termine und freie Plätze werden aktuell direkt bei Carmen erfragt.</p><p>Auch Reitabzeichen, Lehrgänge, Ausritte, Voltigieren und Tage der offenen Stalltür gehören zum bisherigen Hofleben. Die Termine wechseln – die gemeinsame Zeit mit den Pferden bleibt.</p>',
     '<h2>Mehr als nur eine Reitstunde.</h2><p>Ferienreitkurse gehören bei uns schon lange dazu. Dabei wird natürlich geritten, aber auch geputzt, erklärt und viel Zeit mit den Pferden verbracht. Wenn Sie nach einem aktuellen Termin oder einem freien Platz suchen, melden Sie sich bitte direkt bei mir.</p><p>Auch Reitabzeichen, Lehrgänge, Ausritte, Voltigieren und Tage der offenen Stalltür gehören immer wieder zu unserem Hofleben. Die Termine wechseln – die gemeinsame Zeit mit den Pferden bleibt.</p>'),
    ('<h2>Momente, die man nicht in eine Preisliste bekommt.</h2><p>Training, Turniere, Lehrgänge und ganz normale Tage zwischen Stall und Reitplatz. Die Fotostrecke sammelt Motive aus dem bisherigen Seitenbestand und macht sie wieder sichtbar.</p>',
     '<h2>Einblicke in unseren Alltag.</h2><p>Zwischen Unterricht, Turnieren, Lehrgängen und ganz normalen Tagen im Stall entstehen viele schöne Momente. Einige davon habe ich hier gesammelt.</p>'),
    ('<h2>Was bereits passiert ist.</h2><p>Ältere Meldungen bleiben bewusst erhalten. Sie zeigen Erfahrung, Entwicklung und die vielen unterschiedlichen Seiten des Betriebs – statt nach dem Termin einfach zu verschwinden.</p>',
     '<h2>Ein paar Rückblicke aus den vergangenen Jahren.</h2><p>Auch ältere Meldungen dürfen hier bleiben. Sie gehören zur Geschichte der Reitanlage und zeigen, was bei uns über die Jahre alles stattgefunden hat.</p>'),
    ('<h3>Gemeinsam auf Turnieren</h3><p>Aus dem dokumentierten Turnierjahr: A-Dressur, L-Dressur und A**-Springen. Carmen begleitet Schüler, Einsteller und Privatreiter je nach Vereinbarung bei Vorbereitung und Turnierstart.</p>',
     '<h3>Gemeinsam auf Turnieren</h3><p>Aus dem dokumentierten Turnierjahr: A-Dressur, L-Dressur und A**-Springen. Je nach Vereinbarung begleite ich Schüler, Einsteller und Privatreiter bei der Vorbereitung und am Turniertag.</p>'),
    ('<h2>Termine und Verfügbarkeiten am besten direkt abstimmen.</h2>', '<h2>Termine und Verfügbarkeiten stimmen wir am besten direkt ab.</h2>'),
]

replace_many(OUT / 'index.html', index_replacements)
replace_many(OUT / 'aktuelles.html', journal_replacements)

index = (OUT / 'index.html').read_text(encoding='utf-8')
assert 'Was Carmen im Unterricht' not in index
assert 'Schreiben Sie Carmen gern' not in index
assert 'Reiten beginnt für mich mit <em>Vertrauen.</em>' in index
assert 'Was mir beim Reiten <em>wichtig ist.</em>' in index
assert 'melden Sie sich <em>gern bei mir.</em>' in index

print('Applied Carmen voice editorial pass to homepage and Hofjournal.')
