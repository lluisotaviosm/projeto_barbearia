release: python manage.py migrate && python setup_admin.py
web: python setup_admin.py && gunicorn setup.wsgi:application
