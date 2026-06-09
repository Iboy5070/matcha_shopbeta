web: python manage.py migrate --noinput && gunicorn config.wsgi --workers 1 --bind 0.0.0.0:$PORT --timeout 120 --keep-alive 65 --preload
