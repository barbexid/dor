#!/usr/bin/env bash
pkg update -y
pkg install python -y
pkg install python-pillow -y
pip install -r requirements.txt
pip install cryptography
pip install --upgrade rich
