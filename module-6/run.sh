#!/usr/bin/env bash

set -e

cd "$(dirname "$0")"

export LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
export LOCAL_IMAGE_NAME="stream-model-duration:${LOCAL_TAG}"

docker build -t ${LOCAL_IMAGE_NAME} .

docker-compose up -d

sleep 1

aws --endpoint-url=http://localhost:4566 \
    kinesis create-stream \
    --stream-name ride-predictions \
    --shard-count 1

pipenv run python test_docker.py

docker-compose down
