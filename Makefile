BASEDIR=$(CURDIR)
OUTPUTDIR=$(BASEDIR)/static

serve:
	cd $(OUTPUTDIR); python -m SimpleHTTPServer 5555

wcoffee:
	coffee -o static/js -cw coffee/
wsass:
	sass --watch sass:static/css

celery:
	cd watcher;DJANGO_SETTINGS_MODULE=watcher.settings python manage.py celery worker -Q screenshot,day,mail  -l info -B --scheduler djcelery.schedulers.DatabaseScheduler


runserver:
	cd watcher;python manage.py runserver

flower:
	cd watcher;DJANGO_SETTINGS_MODULE=watcher.settings celery -A watcher.tasks flower --port=5556
