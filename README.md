# Mini Fuzz Lab 🧪

**Ein kleines, vollständig lokales Python-Projekt für den Einstieg in Software-Fuzzing.**

Der Fuzzer generiert veränderte Eingaben (Mutation-Based Fuzzing), testet damit
zwei Varianten eines Nachrichten-Parsers, entdeckt einen absichtlich eingebauten
`IndexError`, speichert ein minimiertes Beispiel und zeigt, wie eine korrekte
Eingabevalidierung das Problem behebt.

**Lernprojekt:** Die verwundbare Funktion `parse_buggy` ist absichtlich fehlerhaft.
Dies ist kein Scanner für fremde Webseiten, Server oder Dienste.

## Voraussetzungen

- Python **3.10 oder neuer**
- Keine Drittanbieter-Pakete, kein Netzwerkzugriff erforderlich

## Schnellstart

Öffne ein Terminal im Projektordner `fuzzing-mini-lab`.

### 1. Fehler finden

```bash
python -m mini_fuzz fuzz --target buggy --iterations 2000 --seed 42
```

Beispielausgabe (die genaue Testanzahl kann abweichen):

```text
Target: buggy | Seed: 42
Tests: ... | Gültig: ... | Abgelehnt: ...
Unerwartete Abstürze: 1
  IndexError: b'MSG' -> crashes/crash_IndexError_001.bin
```

> Achtung: Der Befehl endet bei gefundenen Bugs mit Exit-Code `1` – das ist Absicht.

### 2. Fehler reproduzieren und Fix vergleichen

```bash
python -m mini_fuzz replay crashes/crash_IndexError_001.bin
```

Der fehlerhafte Parser löst `IndexError` aus, der korrigierte Parser weist
dieselbe ungültige Eingabe kontrolliert als `InvalidMessage` zurück.

### 3. Korrigierten Parser fuzz-testen

```bash
python -m mini_fuzz fuzz --target fixed --iterations 2000 --seed 42
```

Erwartung: `Unerwartete Abstürze: 0` für diesen endlichen Testlauf.
Das ist **kein Beweis absoluter Sicherheit**.

### 4. Automatische Tests durchführen

```bash
python -m unittest discover -s tests -v
```

Diese Tests laufen auch bei GitHub Actions bei jedem Push.

## 5. Selbst eigene Eingaben testen (interaktiv)

Jetzt kannst du **selbst Nachrichten eingeben** und sofort die Reaktion beider Parser vergleichen:

```bash
python -m mini_fuzz test
```

Dann z. B. Folgendes eingeben (jede Zeile mit Enter bestätigen):

```text
MSG|alice|Hallo
MSG|alice
MSG
HELLO|bob|Test
exit
```

Bei `MSG|alice` zeigt `buggy` einen `IndexError`, während `fixed` die Eingabe
kontrolliert ablehnt. Zum Beenden `exit` eingeben.

Alternativ einen einzigen Test direkt ausführen:

```bash
python -m mini_fuzz test "MSG|alice"
```

**Detaillierte Übungen:** siehe [EIGENE_TESTS.md](EIGENE_TESTS.md).

Wenn der Befehl `python` nicht gefunden wird, unter Windows `py`, unter
macOS/Linux meist `python3` verwenden.

## Wie funktioniert das?

**Testobjekt:** Ein winziger Parser versteht UTF-8-Nachrichten:

```text
MSG|alice|Hallo
```

Eine gültige Nachricht hat drei Felder:

| Feld | Beispiel | Bedeutung |
|---|---|---|
| Nachrichtentyp | `MSG` | Kennung für das Protokoll |
| Absender | `alice` | Name des Absenders |
| Inhalt | `Hallo` | Nachrichtentext |

Die fehlerhafte Variante greift mit `fields[2]` auf das dritte Feld zu, **ohne
vorher die Anzahl der Felder zu überprüfen**. Wird bei einer Mutation das zweite
Trennzeichen entfernt, z. B. `MSG|alice`, entsteht ein `IndexError`.

Der Fuzzer verwendet einen **Seed-Korpus** aus gültigen Nachrichten und verändert
sie zufällig. Unterstützte Mutationen sind Bitflip, Löschen, Einfügen, Ersetzen,
Abschneiden und Duplizieren von Bytes. Ein festgelegter Zufalls-Seed macht den
Testlauf reproduzierbar.

Bei unerwarteten Exceptions wird der Fehlerfall per einfachem **Delta Debugging**
verkleinert. So wird aus dem fehlerhaften Paket z. B. `MSG`, das denselben
`IndexError` auslöst. Die Eingabe wird als Binärdatei unter `crashes/` gespeichert.

**Erwartete Fehlereingaben** (`InvalidMessage`) werden ausdrücklich **nicht** als
Absturz gewertet. Für das reparierte Ziel ist die Feldanzahl validiert, bevor
auf die Einträge zugegriffen wird.

## Verzeichnisstruktur

```text
fuzzing-mini-lab/
├── mini_fuzz/
│   ├── __init__.py       # Python-Paket
│   ├── __main__.py       # Terminal-Befehle
│   ├── protocol.py       # Buggy und Fixed Parser
│   └── engine.py         # Mutationen, Fuzzer, Minimierung
├── tests/
│   ├── test_protocol.py  # Tests für Parser und Fuzzer
│   └── test_cli.py       # 3 Tests für den manuellen Testmodus
├── .github/workflows/
│   └── tests.yml         # GitHub Actions CI
├── .gitignore
├── EIGENE_TESTS.md       # Interaktive Tests Schritt für Schritt
├── INTERVIEW.md          # Kurze Erklärung für das Vorstellungsgespräch
├── DEMO_OUTPUT.txt       # Verifizierte Terminal-Beispielausgabe
├── GITHUB_UPLOAD.md      # Upload-Schritt-für-Schritt
├── LICENSE
└── README.md
```

## Optional: Eigene Experimente

- `--iterations 10000` für mehr Testläufe
- `--seed 123` für eine andere reproduzierbare Mutation-Reihenfolge
- Weitere gültige Nachrichten in `SEED_CORPUS` ergänzen
- Neue Mutationsoperatoren in `mutate()` schreiben
- Zusätzliche Regeln für das Nachrichtenformat im Parser ergänzen

## Grenzen

Dies ist ein **einfacher mutationsbasierter Fuzzer**, kein Coverage-Guided Fuzzer
wie AFL++ und keine Beweisführung für die vollständige Korrektheit einer Software.
Er erkennt vor allem ungefangene Exceptions. Semantische Fehler ohne Exception
müsste man mit zusätzlichen Assertions oder Eigenschaften (Properties) testen.

## Verantwortungsvolle Nutzung

Nur auf eigenen Testprogrammen oder mit ausdrücklicher Erlaubnis testen.
Keine fremden Systeme angreifen. Das Projekt führt alle Tests ausschließlich
lokal an einem eigenen Beispiel-Parser aus.

## Lizenz

MIT – siehe [LICENSE](LICENSE).
