source ~/.freezer.config
cat ~/.freezer.config
if [ "$#" -ne 2 ]; then
    echo usage: $0 albumID folder
    echo zips albumID and adds to Freezer Cache
    exit
fi
ALBUMID=$1
ALBUM_CONTENT=$2

outfile="$FRZR_CACHE/$ALBUMID.zip"
zip -r $outfile "$ALBUM_CONTENT"
echo $ALBUMID	$outfile >> ~/.freezer.content
