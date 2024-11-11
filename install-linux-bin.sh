#!/bin/bash

set -e -x

source "/etc/os-release"
suite="$VERSION_CODENAME"
test -n "$suite"

VERSION="${1?}"

{
    echo deb https://dev.monetdb.org/downloads/deb/ "$suite" monetdb
    echo deb-src https://dev.monetdb.org/downloads/deb/ "$suite" monetdb
} | sudo dd of=/etc/apt/sources.list.d/monetdb.list

sudo wget --output-document=/etc/apt/trusted.gpg.d/monetdb.gpg https://dev.monetdb.org/downloads/MonetDB-GPG-KEY.gpg

sudo apt-get -qy update
sudo apt-get -qy install pkg-config libz-dev

initial_packages=(
    monetdb-server
    monetdb-sql
    monetdb-client
    libmonetdbe-dev
)

# If we ask apt-get to install a specific version of a package we also need
# explicitly install all its dependencies at the right version.
# Because the name of the depencies varies (libmonetdb-stream26/27/28)
# we cannot just put a static list here.
#
# There are commands that recursively resolve the dependencies and there
# are tools that support versions but the following loop is the best
# I could come up with that does both.
packages=("${initial_packages[@]/%/=$VERSION}")
count=0
while test $count -ne ${#packages[@]}; do
    count=${#packages[@]}
    apt depends "${packages[@]}" \
        | sed -n -e '/monet/s/Depends: \([^ ]*\) ([^ ]* \(.*\)).*/\1=\2/p' \
        | tee scratch
    for p in "${packages[@]}"; do
        echo "$p" >>scratch
    done
    packages=($(sed -e 's/ //g' scratch | sort -u))
done

# Now install the full list of packages we determined
sudo apt-get -qy install "${packages[@]}"


# Borrow exact installation directory from libz
echo "prefix=/usr" >>github.output
echo "bindir=$prefix/bin"  >>github.output
echo "includedir=$(pkg-config --variable=includedir zlib)" >>github.output
echo "libdir=$(pkg-config --variable=libdir zlib)" >>github.output
echo "dynsuffix=so" >>github.output

# Start and create database
sudo systemctl enable monetdbd
sudo systemctl start monetdbd
sudo -u monetdb monetdb create -pmonetdb demo monetdb
