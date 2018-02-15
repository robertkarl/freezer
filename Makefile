freezer:
	pyinstaller --onefile freezer.spec
install: freezer
	cp dist/freezer /usr/local/bin/freezer
