#!/bin/bash

set -e -x

DBFARM=/usr/local/dbfarm
#VERSION="${1?}"

# Our Homebrew packaging doesn't seem to support versioning. The article at
# https://cmichel.medium.com/how-to-install-an-old-package-version-with-brew-cc1c567dd088
# suggests that this is something the package maintainers do, not Homebrew
# itself:
#
#     "If the brew package maintainers do versioning this is as easy as typing brew
#     install <packageName>@1.2.3. Often times, there's no versioning system though
#     and the only available version is the latest one."
#
# We should look into this.
# For the time being, however, we'll just blindly install the latest version
# by not running 'brew install monetdb@$VERSION' but simply 'brew install monetdb'.
#
# We'll make sure that the GitHub Action verifies the installed version and errors out
# when there is a mismatch

brew update

brew install monetdb   # @"$VERSION"

sudo mkdir "$DBFARM"
sudo chown "$USER" "$DBFARM"
monetdbd create "$DBFARM"
monetdbd start "$DBFARM"

monetdb create -pmonetdb demo monetdb

prefix="$(brew --prefix)"
echo "prefix=$prefix" >>github.output
echo "bindir=$prefix/bin" >>github.output
echo "includedir=$prefix/include/monetdb" >>github.output
echo "libdir=$prefix/lib" >>github.output
echo "dynsuffix=dylib" >>github.output
