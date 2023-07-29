release: python manage.py migrate
web: daphne -b 0.0.0.0 -p $PORT EatUp.asgi:application
worker: celery -A EatUp worker -l info --concurrency 2