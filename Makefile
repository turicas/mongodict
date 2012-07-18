test:
	@clear
	nosetests -dvs --with-coverage --cover-package mongodict --with-yanc

test-x:
	@clear
	nosetests -dvsx --with-coverage --cover-package mongodict --with-yanc

clean:
	rm -rf MANIFEST build/ dist/ *.egg-info/ reg-settings.py*
	find -regex '.*\.pyc' -exec rm {} \;
	find -regex '.*~' -exec rm {} \;


.PHONY:	test test-x clean
