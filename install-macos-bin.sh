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

echo "bindir=$(brew --prefix)/bin" >>github.output
echo "includedir=$(brew --prefix)/include" >>github.output
echo "libdir=$(brew --prefix)/lib" >>github.output
echo "dynsuffix=dylib" >>github.output
