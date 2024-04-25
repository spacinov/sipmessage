
SRC_DIRS = src/
TEST_DIRS = tests/
PYTHON_DIRS = $(SRC_DIRS) $(TEST_DIRS)

setup-test:
	pip install --upgrade pip setuptools wheel
	pip install --editable .[dev]

.PHONY: setup-test

lint: lint-format lint-ruff

lint-format:
	ruff format --diff $(PYTHON_DIRS) setup.py

lint-pkg:
	check-manifest
	pyroma --directory .

lint-ruff:
	ruff check --diff $(PYTHON_DIRS) setup.py

.PHONY: lint lint-format lint-pkg lint-ruff

test: test-types test-unittest

test-types:
	mypy $(PYTHON_DIRS)

test-unittest:
	coverage run --module unittest discover -vv $(TEST_DIRS)
	coverage report

htmlcov: htmlcov/index.html

htmlcov/index.html: .coverage
	coverage html

.PHONY: htmlcov test test-types test-unittest
