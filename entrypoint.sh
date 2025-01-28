#!/bin/sh
set -e

if [ "$1" = "clear-tags" ]; then
    # Run the clear_tags.py script once
    echo "Running clear_tags.py..."
    python /app/clear_tags.py
else
    # Default to running add_language_tag.py on a schedule
    if [ -z "$INTERVAL_SECONDS" ]; then
        echo "Running add_language_tag.py once."
        python /app/add_language_tag.py
    else
        echo "Running add_language_tag.py every $INTERVAL_SECONDS seconds."
        while true; do
            echo "Running add_language_tag.py at $(date)..."
            python /app/add_language_tag.py
            echo "Waiting for $INTERVAL_SECONDS seconds..."
            sleep "$INTERVAL_SECONDS"
        done
    fi
fi