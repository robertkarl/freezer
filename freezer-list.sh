echo Searching for encrypted data with name \"$1\"
grep --after-context=2 $1 content.txt

