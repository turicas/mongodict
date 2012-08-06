test:
	@clear
	nosetests -dvs --with-coverage --cover-package mongodict --with-yanc

test-x:
	@clear
	nosetests -dvsx --with-coverage --cover-package mongodict --with-yanc

clean:
	rm -rf MANIFEST build/ dist/ *.egg-info/ reg_settings.py* README.html .coverage
	find -regex '.*\.pyc' -exec rm {} \;
	find -regex '.*~' -exec rm {} \;

doc:
	rst2html README.rst > README.html

install:
	python setup.py install

dev:
	pip install -r requirements/develop.txt

upload:
	python setup.py sdist upload

.PHONY:	test test-x doc clean install dev upload
