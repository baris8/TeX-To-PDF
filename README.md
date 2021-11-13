# TeX To PDF

Dieses Packages kann ConTeXt basierte Strings in PDFs kompilieren.
Für die Erstellung der ConTeXt-String kann ein Jinja2-Environment genutzt werden.

Außerdem können noch weitere Anlage-Dateien wie Logos, Hintergründe angegeben werden.
Diese werden, dann beim kompilieren verlinkt und von ConTeXt genutzt.

Vorraussetzung ist, dass auf dem System ConTeXt installiert ist und im `$PATH` gesetzt wurde:
https://wiki.contextgarden.net/ConTeXt_Standalone

Für den Fall das nur die Standalone auf dem System ist, muss folgender Befehl einmal ausgeführt werden:

```
source /installation-dir/tex/setuptex
```

Damit kann ConTeXt dann per Konsolen-Kommando erst aufgerufen werden.


---

Für den direkteren Gebrauch ist die ConTeXt-Setup-Datei hinterlegt unter
`context/first-setup.sh`.

Diese ruft man auf mit `sh ./first-setup.sh --modules=all`
Dadurch wird ConTeXt installiert und steht zur Nutzung bereit.

Falls der Aufruf `context --version` kein Ergebnis liefert, kann man versuchen das Terminal
einmal zu schließen und neu zu öffnen.
Wenn das nicht hilft, dann bitte mit der Anleitung zur Standalone aus dem obigen Link
Systemweit installieren.

# Usage

Für Folgende Ordnerstruktur:

```
templates/
  - context.tex
  - logo.png
main.py
```

Inhalt der `context.tex`:

```
\starttext
Hello world!

{{inhalt|tex_safe}}

\externalfigure[logo.png]

\stoptext
```

Inhalt der `main.py`:

```python
from tex_to_pdf import PDF, Jinja2ENV

env = Jinja2ENV("templates")

# ConTeX-Template rendern
tex_string = env.render("context.tex", inhalt="Hier steht ein gerenderter Text.")
# ConTeX-String rendern
with open('templates/context.tex', 'r') as file:
    raw = file.read()
tex_string = env.render_string(raw, inhalt="Hier steht ein gerenderter Text")

# Den gerenderten TeX-String mit ConTeXt in ein PDF kompilieren und speichern.
dateien = ["templates/logo.png"]
pdf = PDF(tex_string, dateien=dateien)
pdf.speichere_pdf("mein_pdf.pdf", verzeichnis="pdfs")

# Einem PDF Bookmarks hinzufügen
bookmarks = [('Erste Seite', 0)]
pdf.bookmarks_hinzufuegen(bookmarks)
pdf.speichere_pdf("mein_pdf_mit_bookmarks.pdf", verzeichnis="pdfs")
```

Nach ausführen der `main.py` wird ein Ordner `pdfs` angelegt, indem die Dateien `mein_pdf.pdf` und `mein_pdf_mit_bookmarks.pdf` sind.
