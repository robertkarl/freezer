set -e
source ~/.freezer.config

if [ "$#" -ne 2 ]; then
	echo usage: $0 albumID folder
	echo adds encrypted version of stuff in \"folder\" to directory indicated in ~/.freezer.config
	exit
fi
if [ -z $FRZR_CACHE ]; then
	echo please add a FRZR_CACHE variable where unencrypted content can be stored
	exit -1
fi

ALBUMID=$1
ALBUM_CONTENT=$2
outfile="$FRZR_CACHE/$ALBUMID.zip"

zip -rq $outfile "$ALBUM_CONTENT"
fname=$FRZR_CACHE/$1.zip
outputname="$FRZR_EXPORT_FOLDER/$FRZR_PUBKEY.$ALBUMID.zip.gpg"
$FRZR_GPG --batch --yes --output $outputname --encrypt --recipient $FRZR_PUBKEY $fname
printf '%s\n' "$outputname"

