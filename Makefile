
SRC_DIRS = src/
TEST_DIRS = tests/
PYTHON_DIRS = $(SRC_DIRS) $(TEST_DIRS)
PYTHON_FILES = $(shell find $(PYTHON_DIRS) -name '*.py') setup.py

.DEFAULT_GOAL: all

all: test lint

help:
	@echo "Simply run `make` to run all linting and testing tasks."
	@echo ""
	@echo "You may also run `make --jobs 4 --keep-going` for a faster run."
	@echo ""
	@echo "Extra targets:"
	@echo "- ci-lint / ci-test: run tasks for continuous integration"
	@echo "- clean: Remove temporary files"
	@echo "- lint-pkg: Check the packaging setup"
	@echo "- setup-test: Install all development dependencies"

.PHONY: all help


# Cleanup

clean:
	-rm .*-done
	coverage erase

.PHONY: clean

# Dependencies

setup-test: .pip-done


.pip-done: setup.py pyproject.toml
	pip install --upgrade pip setuptools wheel
	pip install --editable .[dev]
	@touch $@

.PHONY: setup-test


# Linting



lint: .ruff-format-done .ruff-check-done

ci-lint: lint lint-pkg

.ruff-format-done: $(PYTHON_FILES) | .pip-done
	ruff format --diff $+
	@touch $@

.ruff-check-done: $(PYTHON_FILES) | .pip-done
	ruff check --diff $+
	@touch $@

lint-pkg:
	check-manifest
	pyroma --directory .

.PHONY: ci-lint lint lint-pkg


# Tests

test: test-types test-unittest

ci-test: test-types xmlcov

test-types: .mypy-done

test-unittest: .coverage

.coverage: $(PYTHON_FILES) | .pip-done
	coverage run --module unittest discover -vv $(TEST_DIRS)
	coverage report

.mypy-done: $(PYTHON_FILES) | .pip-done
	mypy $(PYTHON_DIRS)
	@touch $@

htmlcov: htmlcov/index.html

htmlcov/index.html: .coverage
	coverage html

xmlcov: coverage.xml

coverage.xml: .coverage
	coverage xml

.PHONY: htmlcov xmlcov

.PHONY: ci-test test test-types test-unittest
.PHONY: test test-types test-unittest
