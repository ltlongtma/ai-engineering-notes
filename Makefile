PYTHON ?= python3
TOPICS := $(notdir $(wildcard topics/*))

.PHONY: check lint notes index-check test index export-md site

check: lint notes index-check test

lint:
	$(PYTHON) tools/ste_check.py

notes:
	$(PYTHON) tools/check_notes.py

index-check:
	$(PYTHON) tools/build_index.py --check

test:
	$(PYTHON) -m unittest discover -s tools/tests -t tools

index:
	$(PYTHON) tools/build_index.py

export-md:
	for topic in $(TOPICS) all; do $(PYTHON) tools/export.py --format md --topic $$topic || exit 1; done

site:
	$(PYTHON) tools/build_site.py
