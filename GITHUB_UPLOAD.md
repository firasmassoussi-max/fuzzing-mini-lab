# So veröffentlichst du Mini Fuzz Lab auf deinem GitHub-Profil

## Möglichkeit A: Im Browser (ohne Git-Kenntnisse)

1. ZIP-Datei `fuzzing-mini-lab.zip` herunterladen und **entpacken**.
2. Bei [github.com/new](https://github.com/new) anmelden.
3. Repository-Name: `fuzzing-mini-lab`.
4. Für ein Portfolio **Public** auswählen. Das Repository zunächst **ohne** zusätzliche README oder `.gitignore` erstellen.
5. Im neuen Repository **Add file → Upload files** auswählen.
6. Den **Inhalt** des entpackten Ordners `fuzzing-mini-lab` hochladen, damit `README.md` direkt im Hauptverzeichnis landet. Die Unterordner `mini_fuzz`, `tests` und `.github` mit hochladen.
7. Als Commit-Nachricht `Add Python fuzzing mini lab` eintragen und die Änderungen committen.
8. Kontrollieren, dass auf der Repository-Seite die `README.md` angezeigt wird.

Hilfe von GitHub: https://docs.github.com/de/repositories/working-with-files/managing-files/adding-a-file-to-a-repository

## Möglichkeit B: Über die Kommandozeile (Git + GitHub CLI)

Git und die [GitHub CLI](https://cli.github.com/) müssen installiert sein.
Nach dem Entpacken ein Terminal **im Projektordner** öffnen:

```bash
# Einmal bei GitHub anmelden, falls noch nicht geschehen:
gh auth login

# Repository lokal anlegen und die Dateien speichern:
git init -b main
git add .
git commit -m "Add Python fuzzing mini lab"

# Öffentliches Repository erstellen und die Dateien hochladen:
gh repo create fuzzing-mini-lab --public --source=. --remote=origin --push
```

Wenn Git vor dem Commit nach Name und E-Mail fragt, diese einmal konfigurieren:

```bash
git config --global user.name "DEIN NAME"
git config --global user.email "DEINE GITHUB-EMAIL"
```

Für ein privates Repository im letzten Befehl `--public` durch `--private` ersetzen.

## Wichtige Hinweise

- Kein Passwort oder API-Token in eine Projektdatei schreiben.
- Nicht behaupten, dieses Übungsprojekt sei im Auftrag von softScheck entstanden.
- Auf GitHub wird nur veröffentlicht, wenn **du** den Upload/Push ausführst.
- Bei Windows kann der Python-Befehl `py` statt `python` heißen.
