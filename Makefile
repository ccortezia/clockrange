.PHONY: tests

.DEFAULT_GOAL := build

check:
	pipenv run pre-commit run -a

build: clean
	python setup.py sdist bdist_wheel

test:
	pipenv run pytest .

clean:
	rm -rf dist build clockrange.egg-info
	find . -name "*.pyc" -delete
	rm -f .coverage coverage.xml
	rm -rf htmlcov .pytest_cache __pycache__
	rm -rf .mypy_cache

publish:
	twine upload dist/*

publish.fake:
	twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/*
