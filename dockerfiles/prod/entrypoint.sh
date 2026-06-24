#!/bin/sh

# Apply database migrations
echo "Applying database migrations..."
alembic upgrade heads



# Start the server
echo "Starting server..."
fastapi run --host 0.0.0.0 --port 8000
