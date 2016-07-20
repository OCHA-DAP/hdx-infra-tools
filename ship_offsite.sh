#!/bin/sh

[ -z $HDX_BACKUP_DIR ]      && exit 1
[ -z $HDX_BACKUP_USER ]     && exit 1
[ -z $HDX_BACKUP_SERVER ]   && exit 1
[ -z $HDX_BACKUP_BASE_DIR ] && exit 1
[ -z $HDX_TYPE ]            && exit 1
[ -z $BWLIMIT ]             && exit 1
[ -z $TODAY ]               && exit 1

/srv/tools/helper.sh

rsync -av --progress --bwlimit=$BWLIMIT \
    -e 'ssh -oStrictHostKeyChecking=no' \
    $HDX_BACKUP_DIR/*$TODAY* \
    $HDX_BACKUP_USER@$HDX_BACKUP_SERVER:$HDX_BACKUP_BASE_DIR/$HDX_TYPE/
