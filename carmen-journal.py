from pathlib import Path

path = Path('_site/aktuelles.html')
text = path.read_text(encoding='utf-8')

replacements = [
    ('Was auf dem Hof passiert.', 'Was bei uns auf dem Hof passiert.'),
    ('Aktuelle Hinweise, Ferienkurse, besondere Tage und Erinnerungen aus dem Stallalltag. Hier darf es ausführlicher werden als auf der Startseite – mit mehr Bildern, mehr Rückblicken und mehr von dem, was die Reitanlage ausmacht.',
     'Hier nehme ich Sie ein bisschen ausführlicher mit in unseren Hofalltag: mit aktuellen Hinweisen, Ferienkursen, besonderen Tagen und Erinnerungen aus den vergangenen Jahren.'),
    ('Die wichtigsten Hinweise stehen weiterhin kompakt auf der Startseite. Hier bekommen sie mehr Raum und werden später durch neue Meldungen und Rückblicke ergänzt.',
     'Die wichtigsten Hinweise finden Sie weiterhin kompakt auf der Startseite. Hier gibt es etwas mehr Platz für Neuigkeiten, Bilder und Rückblicke.'),
    ('Ferienreitkurse gehören seit Jahren zum Angebot. Es wird geritten, geputzt, erklärt und natürlich viel Zeit mit den Pferden verbracht. Ein dokumentierter Kurs fand vom 25. bis 28. März 2024 jeweils von 10 bis 16 Uhr statt. Neue Termine und freie Plätze werden aktuell direkt bei Carmen erfragt.',
     'Ferienreitkurse gehören bei uns schon lange dazu. Dabei wird natürlich geritten, aber auch geputzt, erklärt und viel Zeit mit den Pferden verbracht. Wenn Sie nach einem aktuellen Termin oder einem freien Platz suchen, melden Sie sich bitte direkt bei mir.'),
    ('Auch Reitabzeichen, Lehrgänge, Ausritte, Voltigieren und Tage der offenen Stalltür gehören zum bisherigen Hofleben. Die Termine wechseln – die gemeinsame Zeit mit den Pferden bleibt.',
     'Auch Reitabzeichen, Lehrgänge, Ausritte, Voltigieren und Tage der offenen Stalltür gehören immer wieder zu unserem Hofleben. Die Termine wechseln – die gemeinsame Zeit mit den Pferden bleibt.'),
    ('Momente, die man nicht in eine Preisliste bekommt.', 'Einblicke in unseren Alltag.'),
    ('Training, Turniere, Lehrgänge und ganz normale Tage zwischen Stall und Reitplatz. Die Fotostrecke sammelt Motive aus dem bisherigen Seitenbestand und macht sie wieder sichtbar.',
     'Zwischen Unterricht, Turnieren, Lehrgängen und ganz normalen Tagen im Stall entstehen viele schöne Momente. Einige davon habe ich hier gesammelt.'),
    ('Was bereits passiert ist.', 'Ein paar Rückblicke aus den vergangenen Jahren.'),
    ('Ältere Meldungen bleiben bewusst erhalten. Sie zeigen Erfahrung, Entwicklung und die vielen unterschiedlichen Seiten des Betriebs – statt nach dem Termin einfach zu verschwinden.',
     'Auch ältere Meldungen dürfen hier bleiben. Sie gehören zur Geschichte der Reitanlage und zeigen, was bei uns über die Jahre alles stattgefunden hat.'),
    ('Carmen begleitet Schüler, Einsteller und Privatreiter je nach Vereinbarung bei Vorbereitung und Turnierstart.',
     'Je nach Vereinbarung begleite ich Schüler, Einsteller und Privatreiter bei der Vorbereitung und am Turniertag.'),
    ('Termine und Verfügbarkeiten am besten direkt abstimmen.', 'Termine und Verfügbarkeiten stimmen wir am besten direkt ab.'),
]

for old, new in replacements:
    text = text.replace(old, new)

path.write_text(text, encoding='utf-8')

assert 'Hier nehme ich Sie ein bisschen ausführlicher mit in unseren Hofalltag' in text
assert 'Carmen begleitet Schüler, Einsteller und Privatreiter' not in text
print('Applied Carmen voice editorial pass to Hofjournal.')
