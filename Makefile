test: freezerdb_test.py
	python3 freezerdb_test.py
freezer: *.py
	pyinstaller --onefile freezer.spec
install: freezer
	cp dist/freezer /usr/local/bin/freezer
