#!/bin/bash

[ "$1" == "" ] && WORKDIR=~ || WORKDIR=$1

mkdir -p ${WORKDIR}/ms-data/
cat ${WORKDIR}/rsync_pass
touch ${WORKDIR}/rsync_pass
$(which rsync) --password-file=${WORKDIR}/rsync_pass -avz rsync://darthvader@176.32.89.130/msd/SET/ ${WORKDIR}/ms-data/SET/
