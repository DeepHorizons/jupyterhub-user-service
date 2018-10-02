#!/usr/bin/env bash

pipenv install
cd user-service
pipenv run python app.py
