#!/bin/sh

# Run Alembic migrations
echo "Running Alembic migrations..."
alembic upgrade head

# Initialize data
echo "Initializing data..."
python -m app.db.init_data

# Start the application
echo "Starting the application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000