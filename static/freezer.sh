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
source ~/.freezer.config

if [ "$#" -eq 0 ]; then
	echo usage:	$0 list: show content available
	echo usage:	$0 thaw pubkey albumID
	exit
fi

if [ $1 = "list" ]; then
	if [ ! -d "content" ]; then
		echo "No content dir found; freezer needs to be run from the static share dir"
		exit -1
	fi
	cat ./contents.txt
fi

if [ $1 = "thaw" ]; then
	if [ "$#" -ne 3 ]; then
		echo "usage: $0 thaw pubkey albumID"
		echo "please run from the freezer static dir"
		exit -1
	fi
	pubkey=$2
	albumID=$3
	$FRZR_GPG --decrypt "./content/$pubkey.$albumID.zip.gpg" > "$FRZR_DOWNLOAD/$2.zip"
fi
