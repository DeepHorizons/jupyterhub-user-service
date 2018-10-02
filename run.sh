#!/usr/bin/env bash

pip install --pre peewee-async aiohttp peewee aiohttp_jinja2 jinja2 aiopg
cd $PROJECT_DIR
python app.py
