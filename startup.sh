#!/bin/bash

python3 utils/wait_for_postgres.py
if [ $? -ne 0 ]; then
    echo "Postgres isn't ready yet."
    exit 1
fi

python3 utils/wait_for_redis.py
if [ $? -ne 0 ]; then
    echo "Redis isn't ready yet."
    exit 1
fi

gunicorn --workers 4 --bind 0.0.0.0:5001 src.app:app
