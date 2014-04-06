#!/usr/bin/env sh

for i in $(ls ./tests/atoms/); do
    python3 ./tests/atoms/$i/run.py
done
