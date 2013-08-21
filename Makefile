test:
	python setup.py test

flake8:
	flake8 --ignore=E501,E225,E128,W391,W404,F401,F403 --max-complexity 14 viewlet

install:
	python setup.py install

develop:
	python setup.py develop

coverage:
	coverage run --include=viewlet/* setup.py test
