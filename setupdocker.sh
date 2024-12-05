#!/bin/bash

# Helper script for running tests in manylinux containers.
# Our install-linux-bin.sh script assumes wget and sudo have
# been installed but the manylinux container doesn't have those
# out of the box.

set -e -x

apt-get -q -y update
apt-get -q -y install wget sudo

exec ./install-linux-bin.sh "$@"