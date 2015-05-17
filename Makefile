.PHONY: docs test

docs:
	cd docs && make html

test:
	tox -e py27,py34,pypy,flake8,docs

pandastest:
	tox -e py27-pandas,py34-pandas,pypy-pandas
