all:
	pyinstaller --onefile freezer.spec
install:
	cp dest/freezer /usr/local/bin/freezer
