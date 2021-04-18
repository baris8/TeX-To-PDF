# TeX To PDF

Dieses Packages kann ConTeXt basierte Strings in PDFs kompilieren.
Für die Erstellung der ConTeXt-String kann ein Jinja2-Environment genutzt werden.

Außerdem können noch weitere Anlage-Dateien wie Logos, Hintergründe angegeben werden.
Diese werden, dann beim kompilieren verlinkt und von ConTeXt genutzt.

Vorraussetzung ist, dass auf dem System ConTeXt installiert ist und im `$PATH` gesetzt wurde:
https://wiki.contextgarden.net/ConTeXt_Standalone

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

{{inhalt|e}}

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
pdf = pdf.PDF(tex_string, dateien=dateien)
pdf.speichere_pdf("mein_pdf.pdf", verzeichnis="pdfs")

# Einem PDF Bookmarks hinzufügen
bookmarks = [('Erste Seite', 0)]
pdf.bookmarks_hinzufuegen(bookmarks)
pdf.speichere_pdf("mein_pdf_mit_bookmarks.pdf", verzeichnis="pdfs")
```

Nach ausführen der `main.py` wird ein Ordner `pdfs` angelegt, indem die Dateien `mein_pdf.pdf` und `mein_pdf_mit_bookmarks.pdf` sind.
