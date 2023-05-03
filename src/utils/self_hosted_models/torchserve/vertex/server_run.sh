#!/bin/bash
set -x
set -e

# APP_NAME="bloomz-3b" bash server_run.sh

if [ -z $APP_NAME ]; then
    echo "APP_NAME is not set"
    exit 1
fi


torchserve --start \
--ts-config=/home/model-server/config.properties --models \
"$APP_NAME=$APP_NAME.mar" --model-store /home/model-server/model-store