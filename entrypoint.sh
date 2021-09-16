#!/bin/sh

echo "Waiting for postgres..."

if [ "$DATABASE" = "postgres"]
then
    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done
fi

echo "PostgreSQL started"

python manage.py flush --no-input
python manage.py migrate

exec "$@"