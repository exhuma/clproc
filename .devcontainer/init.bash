#!/bin/bash

set -xe

sudo apt-get update && sudo apt-get install -y entr

[ -d env ] || (
    python3 -m venv env && ./env/bin/pip install -U pip
)

./env/bin/pip install -e ".[dev,test]"
