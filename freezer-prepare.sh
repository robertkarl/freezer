set -e
source ~/.freezer.config
if [ "$#" -ne 2 ]; then
	echo usage: $0 albumID folder
	echo zips albumID and adds to Freezer Cache
	exit
fi
if [ -z $FRZR_CACHE ]; then
	echo please add a FRZR_CACHE variable where unencrypted content can be stored
	exit -1
fi
ALBUMID=$1
ALBUM_CONTENT=$2

outfile="$FRZR_CACHE/$ALBUMID.zip"
echo Zipping album content to $outfile
zip -rq $outfile "$ALBUM_CONTENT"
echo $ALBUMID	$outfile >> ~/.freezer.content
cat ~/.freezer.content | sort | uniq > ~/.freezer.content.tmp && mv ~/.freezer.content.tmp ~/.freezer.content
echo Updated ~/.freezer.content file.
