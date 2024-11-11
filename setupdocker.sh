#!/bin/bash

set -e -x

apt-get -q -y update
apt-get -q -y install wget sudo

exec ./install-linux-bin.sh "$@"