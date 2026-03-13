release: python manage.py migrate && python setup_admin.py
web: gunicorn setup.wsgi:application
