export DJANGO_SETTINGS_MODULE=watcher.settings
celery -A watcher.tasks flower --port=5556
