from io import BytesIO
import tempfile
import subprocess
import os
import shutil
import pathlib
from jinja2 import Environment, FileSystemLoader, ChoiceLoader
import logging
from PyPDF2 import PdfFileMerger

log = logging.getLogger(__name__)


class Jinja2ENV:
    """
    Diese Klasse erlaubt es ein Jinja2-Environment Objekt zu erstellen,
    bei welchem man die Dateipfade zu mehreren template-root-Verzeichnissen
    übergeben kann.
    Die Klasse erlaubt es mithilfe der Methode render(template, **kwargs)
    ein Template aus dem definiert Environment zu rendern.
    Außerdem kann mit der Methode render_string(template_string, **kwargs)
    ein String ebenfalls gerendert werden.
    """

    def __init__(self, *args) -> None:
        loader = list()
        for arg in args:
            filesystem_loader = FileSystemLoader(arg)
            loader.append(filesystem_loader)

        self.env = Environment(loader=ChoiceLoader(loader))

    def render(self, template, **kw):
        return self.env.get_template(template).render(**kw)

    def render_string(self, template_string, **kw):
        template = self.env.from_string(template_string)
        return template.render(**kw)


if __name__ == "__main__":
    env = Jinja2ENV("/mnt/d/ubuntu/context letter test/templates", "b")
    print(env.env.loader.list_templates())
