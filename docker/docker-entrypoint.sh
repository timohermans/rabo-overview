#!/bin/sh

echo "Waiting for postgres..."

if [ "$DATABASE" = "postgres" ]
then
    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done
fi

echo "PostgreSQL started"

if [ "$RUN_MIGRATIONS" = "1" ]
then
    echo "Running DB migrations..."
    python manage.py flush --no-input
    python manage.py migrate
    echo "Finished running migrations"
fi

if [ "$DEBUG" = "0" ]
then
    echo "Collecting static files..."
    python manage.py collectstatic
fi

exec "$@"