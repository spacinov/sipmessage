lint: 
	ruff check
	ruff format --check --diff

test:
	coverage erase
	coverage run -m unittest
	coverage report
	coverage xml
