setup-test:
	pip install --upgrade pip setuptools wheel
	pip install --editable .[dev]

.PHONY: setup-test

lint: lint-pkg

lint-pkg:
	check-manifest
	pyroma --directory .

.PHONY: lint lint-pkg
