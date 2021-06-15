#! /bin/bash

echo "Gathering info ..."
MYSQLDIR="$(mysqld --verbose --help 2>/dev/null | awk '$1 == "datadir" { print $2; exit }')"

echo "Checking if MySQL base data exists ..."
if [ ! -d "$MYSQLDIR/mysql" ]; then
    echo "WARNING: Expected the directory $MYSQLDIR/mysql/ to exist -- have you downloaded and unpacked the IETF binary database tarball?"
fi

echo "Starting mysql ..."
/etc/init.d/mysql start

echo "Checking if the IETF database exists at $MYSQLDIR ..."
if [ ! -d "$MYSQLDIR/ietf_utf8" ]; then
    if [ -z "$DATADIR" ]; then
        echo "DATADIR is not set, but the IETF database needs to be set up -- can't continue, exiting the docker init script."
        exit 1
    fi

    if ! /etc/init.d/mysql status; then
        echo "Didn't find the IETF database, but can't set it up either, as MySQL isn't running."
        exit 1
    else
        echo "Loading database ..."
        ./setupdb
    fi
fi

echo "Setting up a default settings_local.py ..."
cp docker/settings_local.py "/root/src/ietf/settings_local.py"

for sub in \
    test/id \
    test/staging \
    test/archive \
    test/rfc \
    test/media \
    test/wiki/ietf \
    data/nomcom_keys/public_keys \
    data/developers/ietf-ftp \
    data/developers/ietf-ftp/charter \
    data/developers/ietf-ftp/conflict-reviews \
    data/developers/ietf-ftp/internet-drafts \
    data/developers/ietf-ftp/rfc \
    data/developers/ietf-ftp/status-changes \
    data/developers/ietf-ftp/yang/catalogmod \
    data/developers/ietf-ftp/yang/draftmod \
    data/developers/ietf-ftp/yang/ianamod \
    data/developers/ietf-ftp/yang/invalmod \
    data/developers/ietf-ftp/yang/rfcmod \
    data/developers/www6s \
    data/developers/www6s/staging \
    data/developers/www6s/wg-descriptions \
    data/developers/www6s/proceedings \
    data/developers/www6 \
    data/developers/www6/iesg \
    data/developers/www6/iesg/evaluation \
    ; do
    dir="/root/src/$sub"
    if [ ! -d "$dir"  ]; then
        echo "Creating dir $dir"
        mkdir -p "$dir";
        chown "$USER" "$dir"
    fi
done

if [ ! -f "/root/src/test/data/draft-aliases" ]; then
    echo "Generating draft aliases ..."
    ietf/bin/generate-draft-aliases
fi

if [ ! -f "/root/src/test/data/group-aliases" ]; then
    echo "Generating group aliases ..."
    ietf/bin/generate-wg-aliases
fi

echo "Done!"

bash