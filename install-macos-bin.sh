#!/bin/bash

set -e -x

DBFARM=/usr/local/dbfarm

# so simple
brew install monetdb

# not so simple, this is a hack
sudo mkdir "$DBFARM"
sudo chown "$USER" "$DBFARM"
monetdbd create "$DBFARM"
monetdbd start "$DBFARM"

monetdb create -pmonetdb demo monetdb

prefix="$(brew --prefix)"
echo "prefix=$prefix" >>github.output
echo "bindir=$prefix/bin" >>github.output
echo "includedir=$prefix/include" >>github.output
echo "libdir=$prefix/lib" >>github.output
echo "dynsuffix=dylib" >>github.output
