#!/bin/bash

set -e -x

source "/etc/os-release"
suite="$VERSION_CODENAME"
test -n "$suite"

{
    echo deb https://dev.monetdb.org/downloads/deb/ "$suite" monetdb
    echo deb-src https://dev.monetdb.org/downloads/deb/ "$suite" monetdb
} | sudo dd of=/etc/apt/sources.list.d/monetdb.list

sudo wget --output-document=/etc/apt/trusted.gpg.d/monetdb.gpg https://dev.monetdb.org/downloads/MonetDB-GPG-KEY.gpg

sudo apt-get -qy update
sudo apt-get -qy install monetdb-server monetdb-client libmonetdbe-dev

# Borrow exact installation directory from libz
sudo apt-get -qy install pkg-config libz-dev
echo "bindir=/usr/bin"  >>github.output
echo "includedir=$(pkg-config --variable=includedir zlib)" >>github.output
echo "libdir=$(pkg-config --variable=libdir zlib)" >>github.output
echo "dynsuffix=so" >>github.output

# Start and create database
sudo systemctl enable monetdbd
sudo systemctl start monetdbd
sudo -u monetdb monetdb create -pmonetdb demo monetdb
