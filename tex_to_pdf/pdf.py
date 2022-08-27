from io import BytesIO
import tempfile
import subprocess
import os
import shutil
import pathlib
import logging
from typing import List, Tuple, Union
from PyPDF2 import PdfFileMerger

log = logging.getLogger(__name__)


def erstelle_temp_directory(tex_string: str) -> str:
    """Erstellt ein TMP-Verzeichnis mit document.tex (deren Inhalt der übergeben tex_string ist)"""
    log.debug(f"Temporäres Verzeichnis mit TeX-Datei erstellt: {tempfile.tempdir}")
    temp_dir = tempfile.mkdtemp()
    datei_pfad = f"{temp_dir}/document.tex"
    with open(datei_pfad, "w", encoding="utf8") as file:
        file.write(tex_string)
    return temp_dir

def symlinke_datei_zu_ordner(src_datei: str, ziel_verzeichnis: str):
    """Erstellt einen SymLink der übergebenen Source-Datei zum Ziel-Verzeichnis"""
    log.debug('SymLinke %s -> %s', src_datei, ziel_verzeichnis)
    src_pfad = pathlib.Path(src_datei)
    datei_name = src_pfad.name
    dst_pfad = pathlib.Path(ziel_verzeichnis, datei_name)
    os.symlink(src_pfad, dst_pfad)

def fuehre_context_aus(cwd: str):
    """
    Render die Datei document.tex im übergeben CurrentWorkingDirectory(cwd)

    Wenn es einen Fehler beim rendern der TeX-Datei gibt -> wirf eine Exception
    """
    log.debug('Führe ConTeXt aus im Ordner: %s', cwd)
    document = subprocess.run(
        ["context", "--nonstop", "--once", "document.tex"],
        cwd=cwd,
        stdout=subprocess.DEVNULL
    )
    # Falls die TeX-Datei nicht kompiliert werden konnte, wird ein Log gesetzt.
    # Das Temp-Directory bleibt erhalten.
    if document.returncode != 0:
        msg = f"Es gab einen Fehler beim kompilieren des PDFs: {cwd}"
        log.exception(msg)
        raise Exception(msg)


class ConTeXtPDFManager:
    @classmethod
    def kompiliere(cls, tex_string: str, datei_pfade: List[str]=None) -> Union[None, bytes]:
        """Erstellt ein Temp-Dir, rendert den übergeben TeX-String in ein PDF und gibt die Bytes zurück"""
        if not tex_string:
            log.warning('TeX-String leer -> erstelle kein PDF')
            return
        if not datei_pfade:
            datei_pfade = []

        temp_dir = erstelle_temp_directory(tex_string)

        for datei_pfad in datei_pfade:
            symlinke_datei_zu_ordner(src_datei=datei_pfad, ziel_verzeichnis=temp_dir)

        try:
            fuehre_context_aus(cwd=temp_dir)
        except Exception:
            log.error('Ausführen von ConTeXt ist fehlgeschlagen -> PDF konnte nicht erstellt werden')
            return

        pdf_datei_pfad = f"{temp_dir}/document.pdf"
        with open(pdf_datei_pfad, "rb") as file:
            pdf_bytes = file.read()

        # Temp-Directory entfernen
        log.debug(f"{temp_dir} entfernen")
        shutil.rmtree(temp_dir)

        return pdf_bytes

    @classmethod
    def speichere_pdf(cls, pdf_bytes: bytes, datei_name: str, verzeichnis: str = None):
        """Speichert die PDF-Bytes unter (verzeichnis/)datei_name"""
        log.info(f'Speichere PDF {datei_name}{f"in {verzeichnis}" if verzeichnis else ""}')
        if not pdf_bytes:
            msg = 'PDF nicht gespeichert, Bytes leer'
            log.error(msg)
        if verzeichnis and not os.path.exists(verzeichnis):
            log.debug("Das Verzeichnis {verzeichnis} anlegen.")
            os.makedirs(verzeichnis)
        if not verzeichnis:
            verzeichnis = ""

        pfad = os.path.join(verzeichnis, datei_name)
        with open(pfad, "wb") as file:
            file.write(pdf_bytes)
            log.info(f"{pfad} gespeichert.")

    @classmethod
    def bookmarks_hinzufuegen(cls, pdf_src: bytes, bookmarks: List[Tuple[str, int]]) -> bytes:
        """
        Erstellt für die angegebene pdf_src Bookmarks, dafür übergibt man ein Liste von Tupeln
        in folgendem Format: [('Bookmark', Seite), ...]
        """
        log.info("Füge dem PDF folgende Bookmarks hinzu: %r", bookmarks)

        pdf = BytesIO(pdf_src)

        output = PdfFileMerger()
        output.append(pdf)

        for text, seite in bookmarks:
            log.debug(f"Füge folgende Bookmark auf Seite {seite} hinzu: {text}")
            output.addBookmark(text, seite, None)

        with BytesIO() as neues_pdf:
            output.write(neues_pdf)
            return neues_pdf.getvalue()
