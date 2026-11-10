SPHINXBUILD ?= sphinx-build
SPHINXOPTS ?= -W --keep-going
.PHONY: html pdf test integration build clean
html:
	$(SPHINXBUILD) $(SPHINXOPTS) -b html docs docs/_build/html
pdf:
	$(SPHINXBUILD) $(SPHINXOPTS) -b simplepdf docs docs/_build/pdf
test:
	pytest tests/unit tests/smoke
integration:
	pytest tests/integration
build:
	python -m build
	python -m twine check dist/*
clean:
	rm -rf docs/_build build dist
