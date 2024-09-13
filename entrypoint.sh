#!/bin/bash

# Ensure PostgreSQL is ready to accept connections
export PGPASSWORD=$DB_PASS
until psql -h "$DB_HOST" -U "$DB_USER" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

# Run Alembic migrations
poetry run alembic upgrade head

# Execute the SQL script
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f init.sql

# Start the application
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
