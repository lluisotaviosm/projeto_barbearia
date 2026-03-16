release: python manage.py migrate && python promote_admin.py
web: python manage.py migrate && gunicorn setup.wsgi:application
