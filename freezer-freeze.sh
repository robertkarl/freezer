set -e
set -x
source ~/.freezer.config
set +x
if [ "$#" -ne 2 ]; then
    echo usage: $0 pubkey albumID
    echo looks up albumID and encrypts for pubkey
    exit
fi
fname=$( grep $2 ~/.freezer.content | awk '{print $2}' )
echo unencrypted version lives at $fname
set -x
outputname="/Users/rk/Dropbox/Albums/$1.$2.zip.gpg"
set +x
echo exporting file to $outputname
$GPG --output $outputname --encrypt --recipient $1 $fname
