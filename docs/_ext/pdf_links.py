"""Resolve Sphinx document-qualified fragments in the single-file PDF manual."""

from bs4 import BeautifulSoup
from sphinx_simplepdf.builders.simplepdf import SimplePdfBuilder


class LinkedPdfBuilder(SimplePdfBuilder):
    def _toctree_fix(self, index_html):
        soup = BeautifulSoup(super()._toctree_fix(index_html), "html.parser")
        targets = {element["id"] for element in soup.select("[id]")}
        for link in soup.select("a[href]"):
            href = link["href"]
            if href.startswith("#document-") and href.count("#") > 1:
                target = href.rsplit("#", 1)[1]
                if target in targets:
                    link["href"] = "#" + target
        return str(soup)


def setup(app):
    app.setup_extension("sphinx_simplepdf.builders.simplepdf")
    app.add_builder(LinkedPdfBuilder, override=True)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
