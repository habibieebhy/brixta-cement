.PHONY: install test lint build check example clean

PACKAGE := packages/cement-aas

install:
	python -m pip install -e "$(PACKAGE)[dev]"

test:
	python -m pytest $(PACKAGE)/tests -q

lint:
	python -m ruff check $(PACKAGE)/src $(PACKAGE)/tests examples

build:
	rm -rf $(PACKAGE)/dist $(PACKAGE)/build
	python -m build $(PACKAGE)
	python -m twine check $(PACKAGE)/dist/*

check: lint test build

example:
	python examples/reference_pyro_line.py

clean:
	rm -rf $(PACKAGE)/dist $(PACKAGE)/build
