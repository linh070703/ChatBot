#!/bin/bash
set -x
set -e

if [ ! -d "torchserve" ]; then
    echo 'Please run this script in the root directory of the project'
    exit 1
fi

model_name="chatbot"
checkpoint="models/bigscience/bloomz-3b"

if [ ! -d "$checkpoint" ]; then
    echo "$checkpoint not found"
    exit 1
fi

find . | egrep "\.(py)$" | zip -@ module.zip

torch-model-archiver -f \
--model-name $model_name \
--version 1.0 \
--serialized-file $checkpoint/pytorch_model.bin \
--handler torchserve/torchserve_handler.py \
--extra-files \
"$checkpoint/config.json,\
$checkpoint/added_tokens.json,\
$checkpoint/spiece.model,\
$checkpoint/config.json,\
$checkpoint/tokenizer_config.json,\
$checkpoint/generation_config.json,\
$checkpoint/special_tokens_map.json,\
$checkpoint/tokenizer.json,\
module.zip"

mkdir -p model_store

mv $model_name.mar model_store/
rm module.zip

torchserve --stop

torchserve --start \
--model-store model_store \
--ts-config torchserve/config.properties \
--ncs --models $model_name=$model_name.mar