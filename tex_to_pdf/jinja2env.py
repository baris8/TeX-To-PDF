from jinja2 import Environment, FileSystemLoader, ChoiceLoader
from decimal import Decimal
import logging

log = logging.getLogger(__name__)


def tex_safe(s):
    """
    Quotet Unicode-Strings so, dass sie literal als TeX-String
    dargestellt werden.
    """
    if isinstance(s, (int, Decimal)):
        s = str(s)
    elif not isinstance(s, str):
        return ""

    return s.translate(
        {
            ord(u"|"): u"\\|",
            ord(u"&"): u"\\&",
            ord(u"%"): u"\\%",
            ord(u"$"): u"\\$",
            ord(u"#"): u"\\#",
            ord(u"_"): u"\\_",
            ord(u"{"): u"\\{",
            ord(u"}"): u"\\}",
            ord(u"~"): u"\\textasciitilde{}",
            ord(u"^"): u"\\textasciicircum{}",
            ord(u"\\"): u"\\textbackslash{}",
        }
    )


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
        self.env.filters["tex_safe"] = tex_safe

    def render(self, template, **kw):
        return self.env.get_template(template).render(**kw)

    def render_string(self, template_string, **kw):
        template = self.env.from_string(template_string)
        return template.render(**kw)
