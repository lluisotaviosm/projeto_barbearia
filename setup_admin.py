import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from users.models import CustomUser
from core.models import Barbeiro

def create_official_admin():
    email = 'admin@monteiro.com'
    password = 'Monteiro03_' # Senha fornecida pelo usuario
    
    if not CustomUser.objects.filter(email=email).exists():
        print(f"CRIANDO SUPERUSUARIO OFICIAL: {email}...")
        user = CustomUser.objects.create_superuser(
            email=email,
            username='admin_monteiro',
            password=password,
            nome_completo='Luis Otavio (Dono)',
            telefone='55' # Sera ajustado depois no painel
        )
        print("CONTA CRIADA!")
    else:
        user = CustomUser.objects.get(email=email)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        print(f"USUARIO {email} JA EXISTE. PERMISSOES ATUALIZADAS.")

    # Garantir que ele tambem seja Barbeiro no sistema
    Barbeiro.objects.get_or_create(
        user=user,
        defaults={'bio': 'Dono e Administrador da Barbearia'}
    )
    print("PERFIL DE BARBEIRO CONECTADO!")

if __name__ == '__main__':
    create_official_admin()
