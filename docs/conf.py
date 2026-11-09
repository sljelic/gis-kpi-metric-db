from pathlib import Path
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs/_ext"))
metadata = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
project = "GIS KPI Metric Database"
release = version = metadata["version"]
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_simplepdf",
    "pdf_links",
]
master_doc = "index"
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
exclude_patterns = ["_build", "_generated"]
html_theme = "pydata_sphinx_theme"
html_theme_options = {"github_url": "https://github.com/sljelic/gis-kpi-metric-db"}
simplepdf_file_name = f"gis-kpi-metric-db-{release}.pdf"
