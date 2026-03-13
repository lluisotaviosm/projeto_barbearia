release: python manage.py migrate && python setup_admin.py
web: python manage.py migrate && gunicorn setup.wsgi:application
