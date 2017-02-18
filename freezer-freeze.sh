set -e
cat ~/.freezer.config
source ~/.freezer.config
if [ "$#" -ne 2 ]; then
    echo usage: $0 pubkey albumID
    echo looks up albumID and encrypts for pubkey
    exit
fi
fname=$( grep $2 ~/.freezer.content | awk '{print $2}' )
echo Content with ID $2 exists unencrypted at $fname
outputname="$FRZR_EXPORT_FOLDER/$1.$2.zip.gpg"
echo exporting file to $outputname
$FRZR_GPG --batch --yes --output $outputname --encrypt --recipient $1 $fname
