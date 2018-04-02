web: gunicorn dnc_db.wsgi --log-file -
worker: celery -A dnc_db worker -Q data_sending -l info
beat: celery -A dnc_db beat -l info
