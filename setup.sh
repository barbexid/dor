#!/usr/bin/env bash
pkg update -y
pkg install python -y
pkg install python-pillow -y
pkg install libandroid-support -y
pip install -r requirements.txt
pip install --upgrade rich
