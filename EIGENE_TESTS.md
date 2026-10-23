# Eigenes Fuzzing-Experiment – Schritt für Schritt

Mit diesen Experimenten kannst du die Eingaben selbst wählen. Alle Programme laufen lokal auf deinem Rechner und greifen nicht auf fremde Systeme zu.

## Start

1. Installiere Python 3.10 oder neuer.
2. Entpacke das ZIP und öffne ein Terminal **im Ordner `fuzzing-mini-lab`**.
3. Starte den interaktiven Modus:

```bash
python -m mini_fuzz test
```

Wenn `python` nicht funktioniert: unter Windows `py`, unter macOS/Linux `python3` verwenden.

## Übung 1: Eine gültige Nachricht

Gib diese Zeile ein und drücke Enter:

```text
MSG|alice|Hallo
```

Beide Parser sollten eine Nachricht mit dem Absender `alice` akzeptieren.

## Übung 2: Den Fehler selbst auslösen

Gib ein:

```text
MSG|alice
```

**Erwartung:** `buggy` zeigt `CRASH -> IndexError`; `fixed` zeigt `kontrolliert abgelehnt`.

Probiere danach `MSG` – auch hier ist die fehlende Feldzahl das Problem.

## Übung 3: Was passiert bei falschem Format?

Teste die folgenden Eingaben nacheinander:

```text
HELLO|alice|Hallo
MSG||Hallo
MSG|bob|
MSG|alice|Hallo|Welt
```

Beobachte, welche Eingaben akzeptiert oder abgelehnt werden. Die letzte Zeile wird derzeit als Nachricht mit dem Inhalt `Hallo|Welt` behandelt, weil maximal zweimal getrennt wird (`maxsplit=2`).

## Übung 4: Zufallstests laufen lassen

Beende den interaktiven Modus mit `exit`. Starte danach:

```bash
python -m mini_fuzz fuzz --target buggy --iterations 2000 --seed 42
python -m mini_fuzz replay crashes/crash_IndexError_001.bin
python -m mini_fuzz fuzz --target fixed --iterations 2000 --seed 42
```

**Hinweis:** Die erste Ausführung kann mit Exit-Code 1 enden – das bedeutet hier, dass der Fuzzer einen Bug entdeckt hat.

## Übung 5: Eigene Idee untersuchen

Öffne `mini_fuzz/protocol.py`. Füge bei `parse_fixed` eine weitere Regel für erlaubte Absender hinzu. Lege in `tests/test_protocol.py` einen neuen Testfall an und starte:

```bash
python -m unittest discover -s tests -v
```

## Testen mit einem einzigen Terminal-Befehl

Wenn du den Dialogmodus nicht verwenden willst:

```bash
python -m mini_fuzz test "MSG|alice"
```

**Für das Interview:** Erkläre, weshalb `IndexError` einen ungeplanten Absturz darstellt und warum eine kontrollierte `InvalidMessage`-Exception besser ist. Der absichtlich eingebaute Fehler dient nur dem Lernen.
