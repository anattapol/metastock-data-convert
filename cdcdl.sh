#!/bin/bash
RSYNC=$(which rsync)
$RSYNC --password-file=~/rsync_pass -avz rsync://darthvader@176.32.89.130/msd/SET/ ~/ms-data/SET/
