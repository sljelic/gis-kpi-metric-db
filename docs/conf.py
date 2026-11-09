from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'_ext'))
project='GIS KPI Database Deployment'
extensions=['myst_parser','sphinx.ext.autodoc','sphinx_simplepdf','pdf_links']
master_doc='index'
exclude_patterns=['_build']
html_theme='alabaster'
simplepdf_file_name='gis-kpi-database-deployment.pdf'
