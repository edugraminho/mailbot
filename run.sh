#!/bin/bash
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

while true; do
    python3 run.py
    sleep 5
done
