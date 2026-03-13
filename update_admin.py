import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

User = get_user_model()
try:
    admin_user = User.objects.get(email='admin@mineiro.com')
    admin_user.set_password('Monteiro03_')
    admin_user.save()
    print("Senha do administrador alterada com sucesso!")
except User.DoesNotExist:
    # Se não existe, cria com a nova senha
    User.objects.create_superuser(
        email='admin@mineiro.com',
        username='admin',
        password='Monteiro03_',
        nome_completo='Administrador',
        telefone='11999999999'
    )
    print("Administrador não existia e foi criado com a nova senha.")
