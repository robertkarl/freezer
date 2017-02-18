if [ "$#" -ne 2 ]; then
    echo usage: $0 albumID folder
    echo zips albumID and adds to Freezer Cache
    exit
fi
ALBUMID=$1
ALBUM_CONTENT=$2

zip -r "$FRZR_CACHE/$ALBUMID.zip" "$ALBUM_CONTENT"
