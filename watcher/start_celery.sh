set -x
python manage.py celery worker -A watcher.tasks -l info -B --scheduler djcelery.schedulers.DatabaseScheduler
