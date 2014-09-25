test:
	python setup.py test

flake8:
	flake8 viewlet

install:
	python setup.py install

develop:
	python setup.py develop

coverage:
	coverage run --source viewlet setup.py test

clean:
	rm -rf .tox/ dist/ *.egg *.egg-info .coverage
