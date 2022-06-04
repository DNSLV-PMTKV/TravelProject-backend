release: python manage.py migrate
web: gunicorn config.wsgi:application --error-logfile - --log-level info