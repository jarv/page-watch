rm -f watcher/migrations/*
python manage.py makemigrations --empty watcher
python manage.py migrate
python manage.py makemigrations
python manage.py migrate

aws s3 rm s3://page-watch-day --recursive
aws s3 rm s3://page-watch-week --recursive
aws s3 rm s3://page-watch-hour --recursive

echo "from django.db import DEFAULT_DB_ALIAS as database; from django.contrib.auth.models import User; User.objects.db_manager(database).create_superuser('jarv', '', 'radiogaga')"  | ./manage.py shell
