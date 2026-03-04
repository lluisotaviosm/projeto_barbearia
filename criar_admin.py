import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbearia_prj.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@email.com', 'suasenha123')
    print("Superusuário criado com sucesso!")
else:
    print("Superusuário já existe.")