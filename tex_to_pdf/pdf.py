from io import BytesIO
import tempfile
import subprocess
import os
import shutil
import pathlib
import logging
from PyPDF2 import PdfFileMerger

log = logging.getLogger(__name__)


class PDF:
    def __init__(
        self,
        tex_string,
        dateien=None,
    ) -> None:
        self.tex_string = tex_string
        self.dateien = list()
        if dateien:
            self.dateien = dateien
        self.pdf_bytes = None

    def kompiliere_pdf(self):
        log.info("Kompiliere das PDF mit folgenden Dateien: %r", self.dateien)
        if not self.tex_string:
            log.exception("Eine TeX-Source muss anegegeben werden.")
            raise ValueError

        # TeX-Datei im Temp-Directory erstellen
        temp_dir = tempfile.mkdtemp()
        datei_pfad = f"{temp_dir}/document.tex"
        with open(datei_pfad, "w", encoding="utf8") as file:
            file.write(self.tex_string)
        log.debug(
            "Temporäres Verzeichnis mit TeX-Datei erstellt: %s",
            tempfile.tempdir
        )

        # Zusätzliche Dateien als Sym-Link abspeichern
        for datei in self.dateien:
            src_pfad = pathlib.Path(f"{datei}")
            dst_pfad = pathlib.Path(f"{temp_dir}/{str(datei).split('/')[-1]}")
            os.symlink(src_pfad, dst_pfad)

        document = subprocess.run(
            ["context", "--nonstop", "--once", "document.tex"], cwd=temp_dir
        )

        # Falls die TeX-Datei nicht kompiliert werden konnte,
        # wird ein Log gesetzt.
        # Das Temp-Directory bleibt erhalten.
        if document.returncode != 0:
            log.exception(
                "Es gab einen Fehler beim kompilieren des PDFs: %s",
                temp_dir
            )
            return

        pdf_datei_pfad = f"{temp_dir}/document.pdf"
        with open(pdf_datei_pfad, "rb") as file:
            pdf_bytes = file.read()

        # Temp-Directory entfernen
        log.debug(f"{temp_dir} entfernen")
        shutil.rmtree(temp_dir)

        self.pdf_bytes = pdf_bytes

    def bookmarks_hinzufuegen(self, bookmarks):
        log.info("Füge dem PDF folgende Bookmarks hinzu: %r", bookmarks)
        if not self.pdf_bytes:
            log.warning(
                "Es existieren noch keine PDF-Bytes, "
                "daher wird das PDF kompiliert"
            )
            self.kompiliere_pdf()

        pdf = BytesIO(self.pdf_bytes)

        output = PdfFileMerger()
        output.append(pdf)

        for text, seite in bookmarks:
            log.debug(
                "Füge folgende Bookmark auf Seite %s hinzu: %s",
                seite, text
            )
            output.addBookmark(text, seite, None)

        with BytesIO() as neues_pdf:
            output.write(neues_pdf)
            self.pdf_bytes = neues_pdf.getvalue()

    def speichere_pdf(self, dateiname, verzeichnis=None):
        log.info(
            "Speichere das PDF %r in folgendem Verzeichnis %r",
            dateiname, verzeichnis
        )
        if not self.pdf_bytes:
            log.warning(
                "Es existieren noch keine PDF-Bytes, "
                "daher wird das PDF kompiliert"
            )
            try:
                self.kompiliere_pdf()
            except ValueError:
                log.exception(
                    "Das PDF konnte nicht gespeichert werden, "
                    "da der TeX-String leer war."
                )

        if verzeichnis and not os.path.exists(verzeichnis):
            log.debug("Das Verzeichnis {verzeichnis} anlegen.")
            os.makedirs(verzeichnis)
        if not verzeichnis:
            verzeichnis = ""

        pfad = os.path.join(verzeichnis, dateiname)
        with open(pfad, "wb") as file:
            file.write(self.pdf_bytes)
            log.info(f"{file.name} wurde gespeichert.")
