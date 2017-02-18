set -e
echo $#
if [ "$#" -ne 2 ]; then
    echo usage: $0 pubkey albumID
    echo looks up albumID and encrypts for pubkey
    exit
fi
fname=$( grep $2 ~/.freezer.content | awk '{print $2}' )
echo unencrypted version lives at $fname
outputname="/Users/rk/Dropbox/Albums/$1.$2.zip.gpg"
echo exporting file to $outputname
gpg2 --output $outputname --encrypt --recipient $1 $fname
