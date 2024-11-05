#!/bin/bash

# Exit on any error
set -e

if [ ! -d "migrations" ]; then
    echo "Initializing database..."
    flask db init
else
    echo "Database already initialized."
fi

# Check if there are any new migrations to apply
if flask db migrate -m "Running migrations"; then
    echo "Running upgrades..."
    flask db upgrade
else
    echo "No new migrations to apply."
fi
# Run the main application
exec "$@"
