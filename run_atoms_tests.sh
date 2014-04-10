#!/usr/bin/env sh

for i in $(ls ./tests/atoms/); do
    echo "running: $i"
    python3 ./tests/atoms/$i/run.py
done
