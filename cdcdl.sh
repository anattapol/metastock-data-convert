#!/bin/bash -xe

[ "$1" == "" ] && WORKDIR=~ || WORKDIR=$1

mkdir -p ${WORKDIR}/ms-data/
chmod 400 ${WORKDIR}/rsync_pass
chown jenkins ${WORKDIR}/rsync_pass
/usr/bin/rsync --password-file=${WORKDIR}/rsync_pass -avz rsync://darthvader@176.32.89.130/msd/SET/ ${WORKDIR}/ms-data/SET/
