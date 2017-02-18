if [ "$#" -ne 2 ]; then
    echo usage: $0 pubkey albumID
    exit
fi
gpg --decrypt "/home/rk/Dropbox/Albums/$1.$2.zip.gpg" > "$1.$2"
