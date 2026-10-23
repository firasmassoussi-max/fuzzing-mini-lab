# Vorstellungsgespräch: So erkläre ich mein Fuzzing-Projekt

## Meine Erklärung (30–45 Sekunden)

„Ich habe einen kleinen mutationsbasierten Fuzzer in Python gebaut. Er nimmt
gültige Beispielnachrichten und verändert zufällig einzelne Bytes. Damit teste
ich einen Nachrichten-Parser auf unerwartete Programmfehler. Der Fuzzer hat einen
`IndexError` entdeckt, wenn eine Nachricht zu wenige Trennzeichen enthält.
Danach habe ich den Fehlerfall minimiert, einen Regressionstest geschrieben
und im korrigierten Parser die Anzahl der Felder vor dem Zugriff überprüft.
Der Fuzzer läuft anschließend mit demselben Seed ohne unerwarteten Absturz.“

## Was habe ich dabei gelernt?

1. **Fuzzing:** Viele automatisch erzeugte oder mutierte Eingaben testen.
2. **Seed-Korpus:** Kleine Sammlung gültiger Start-Eingaben.
3. **Mutation:** Einfügen, Löschen oder Ändern von Bytes.
4. **Crash vs. Ablehnung:** `IndexError` ist unerwartet; `InvalidMessage` ist kontrolliert.
5. **Reproduzierbarkeit:** `--seed 42` erzeugt denselben Pseudozufallsablauf.
6. **Minimierung:** Unnötige Bytes entfernen, bis der kleinste einfache Fehlerfall übrig bleibt.
7. **Regressionstest:** Der Test verhindert, dass derselbe Bug unbemerkt wiederkommt.

## Drei Fragen, die ich beantworten kann

**Warum fuzzing und nicht nur Unit-Tests?**
Unit-Tests prüfen bekannte Fälle. Fuzzing erzeugt viele ungewöhnliche Eingaben,
die ich nicht alle manuell vorhersehe. Beides ergänzt sich.

**Ist das Projekt wie AFL++?**
Nein. Mein Projekt ist ein einfacher mutationsbasierter Fuzzer ohne
Coverage-Steuerung. Ich kann aber erklären, welche Funktion Coverage-Guided
Fuzzing zusätzlich hat: Neue Testfälle werden anhand neuer erreichter
Programm-Pfade priorisiert.

**Was sind die Grenzen?**
Ein Lauf mit 0 Abstürzen beweist nicht, dass keine Bugs existieren. Außerdem
können logische Fehler auftreten, ohne eine Exception auszulösen. Dafür wären
zusätzliche Invarianten oder Assertions nötig.

## Live-Demo in 3 Kommandos

```bash
python -m mini_fuzz fuzz --target buggy --iterations 2000 --seed 42
python -m mini_fuzz replay crashes/crash_IndexError_001.bin
python -m mini_fuzz fuzz --target fixed --iterations 2000 --seed 42
```

**Hinweis:** Beim ersten Befehl ist der Exit-Code `1` beabsichtigt, weil ein
unerwarteter Absturz gefunden wurde.

## Ehrlich darstellen

Der Bug in `parse_buggy` wurde für die Lern-Demo absichtlich eingebaut. Ich kann
erklären, wie der Fuzzer ihn reproduziert und wie die Fehlerbehebung funktioniert.
Das Projekt wurde nicht bei softScheck intern durchgeführt und ist kein echter
Sicherheitstest an einem Unternehmenssystem.
