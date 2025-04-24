all: test lint lint-pkg

clean:
	rm -rf .coverage .mypy_cache .ruff_cache docs/_build htmlcov

lint:
	ruff check --diff
	ruff format --diff
	mypy src tests

lint-pkg:
	check-manifest
	pyroma --directory .

setup-test:
	pip install --editable .[dev]

test:
	coverage erase
	coverage run -m unittest discover -v
	coverage html
	coverage report --fail-under=100
