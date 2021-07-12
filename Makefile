.PHONY: qa quality mypy test coverages coverage_report coverage_html pylint pyroma

quality:
	isort sopel_lichess
	isort tests
	flake8

test:
	coverage run -m py.test -v .

coverage_report:
	coverage report

coverage_html:
	coverage html

coverages: coverage_report coverage_html

pylint:
	pylint sopel_lichess tests

pyroma:
	pyroma .

mypy:
	mypy sopel_lichess

qa: quality mypy test coverages pylint pyroma

.PHONY: develop build

develop:
	pip install -U pip
	pip install -U -r requirements.txt
	python setup.py develop

build:
	rm -rf build/ dist/
	python setup.py sdist bdist_wheel
