import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from users.models import CustomUser
from core.models import Barbeiro

def setup_admins():
    admins = [
        {'email': 'admin@monteiro.com', 'username': 'admin_monteiro'},
        {'email': 'admin@mineiro.com', 'username': 'admin_mineiro'},
    ]
    password = 'Monteiro03_'
    
    for admin_data in admins:
        email = admin_data['email']
        username = admin_data['username']
        
        if not CustomUser.objects.filter(email=email).exists():
            print(f"CRIANDO ADMIN: {email}...")
            user = CustomUser.objects.create_superuser(
                email=email,
                username=username,
                password=password,
                nome_completo='Luis Otavio (Dono)',
                telefone='5511999999999'
            )
        else:
            print(f"ATUALIZANDO ADMIN: {email}...")
            user = CustomUser.objects.get(email=email)
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.set_password(password)
            user.save()
            
        # Garantir Perfil de Barbeiro
        Barbeiro.objects.get_or_create(user=user, defaults={'bio': 'Dono e Administrador'})
        print(f"OK: {email} pronto para login.")

if __name__ == '__main__':
    setup_admins()
