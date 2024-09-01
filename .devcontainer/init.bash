#!/bin/bash

set -xe

[ -d env ] || (
    python3 -m venv env && ./env/bin/pip install -U pip
)

./env/bin/pip install -e ".[dev,test]"
