set -e
echo Importing freezer config.
source ~/.freezer.config
if [ "$#" -ne 2 ]; then
    echo usage: $0 pubkey albumID
    echo looks up albumID in the cache and encrypts for given pubkey
    exit
fi
fname=$( grep $2 ~/.freezer.content | awk '{print $2}' )
if [ -z "$fname" ]; then
	echo "no cached content for album $2; please try freezer-preparing it."
	exit
fi
echo Found matching unencrypted file at $fname
outputname="$FRZR_EXPORT_FOLDER/$1.$2.zip.gpg"
echo Exporting encrypted version to $outputname
$FRZR_GPG --batch --yes --output $outputname --encrypt --recipient $1 $fname
