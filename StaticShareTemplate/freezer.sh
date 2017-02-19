#!/bin/bash
setup_deps() {
	if command -v gpg >/dev/null 2>&1; then
		echo FRZR_GPG=gpg >> ~/.freezer.config.tmp
	elif command -v gpg2 >/dev/null 2>&1 ; then
		echo FRZR_GPG=gpg2 >> ~/.freezer.config.tmp
	else
		echo Freezer requires gpg or gpg2. Please install.
		rm ~/.freezer.config.tmp
		exit -1
	fi
}

if [ ! -f ~/.freezer.config ];
then
	echo Welcome to Freezer. Creating a config file in ~/.freezer.config and populating with some sane defaults.
	touch ~/.freezer.config.tmp
	echo By  default content downloaded with freezer will be stored in ~/Downloads
	echo FRZR_DOWNLOAD=~/Downloads >> ~/.freezer.config.tmp
	setup_deps
	mv ~/.freezer.config.tmp ~/.freezer.config
	echo Setup succeeded. 
	exit
fi

if [ "$#" -eq 0 ]; then
	echo usage:	$0 list: show content available
	exit
fi
$GPG --decrypt "/home/rk/Dropbox/Albums/$1.$2.zip.gpg" > "$1.$2"
