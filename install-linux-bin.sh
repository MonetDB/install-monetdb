    #!/bin/bash

set -e -x

REQUESTED_MONETDB_VERSION="${1?}"
START_MONETDB="${2-true}"

DBFARM=""

install_debs() {
    source "/etc/os-release"
    suite="$VERSION_CODENAME"
    test -n "$suite"

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
    packages=("${initial_packages[@]/%/=$REQUESTED_MONETDB_VERSION}")
    count=0
    while test $count -ne ${#packages[@]}; do
        count=${#packages[@]}
        apt depends "${packages[@]}" \
            | sed -n -e '/monet/s/Depends: \([^ ]*\) ([^ ]* \(.*\)).*/\1=\2/p' \
            | tee /tmp/scratch
        for p in "${packages[@]}"; do
            echo "$p" >>/tmp/scratch
        done
        packages=($(sed -e 's/ //g' /tmp/scratch | sort -u))
    done

    # Now install the full list of packages we determined
    sudo apt-get -qy install "${packages[@]}"
}


install_rpms() {
    yum -y install sudo   # needed in manylinux container
    yum -y install https://dev.monetdb.org/downloads/epel/MonetDB-release-epel.noarch.rpm
    rpm --import https://dev.monetdb.org/downloads/MonetDB-GPG-KEY
    pkgs=(
        MonetDB-SQL
        MonetDB-server
        MonetDB-client
        MonetDB-embedded
        MonetDB-devel
        MonetDB-embedded-devel
    )
    yum -y install "${pkgs[@]/%/-$REQUESTED_MONETDB_VERSION}"
}


# Install the packages
if type -P yum >/dev/null; then
    install_rpms
    DBFARM=/usr/local/dbfarm
elif type -P apt-get >/dev/null; then
    install_debs
    DBFARM=/var/monetdb5/dbfarm
else
    echo 'Cannot find yum or apt-get'
    exit 1
fi


# Print metadata
echo "prefix=/usr" >>github.output
echo "bindir=/usr/bin"  >>github.output
echo "includedir=/usr/include/monetdb" >>github.output
echo "libdir=$(pkg-config --variable=libdir monetdbe)" >>github.output
echo "dynsuffix=so" >>github.output


# Leave early if we don't have to start a daemon
if [ 'true' != "$START_MONETDB" ]; then
    exit 0
fi

# Start and create database
#sudo systemctl enable monetdbd
if sudo systemctl start monetdbd; then
    # running on a 'real' host
    true
else
    # probably running in a container where pid 1 is not systemd
    DBFARM=/usr/local/dbfarm
    sudo mkdir "$DBFARM"
    sudo chown monetdb:monetdb "$DBFARM"
    sudo -u monetdb monetdbd create "$DBFARM"
    sudo -u monetdb monetdbd start "$DBFARM"
    echo "dbfarm=$DBFARM" >>github.output
fi

sudo -u monetdb monetdb create -pmonetdb demo monetdb

echo "dbfarm=$DBFARM" >>github.output
