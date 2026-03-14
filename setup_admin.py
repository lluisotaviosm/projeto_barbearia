import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from users.models import CustomUser
from core.models import Barbeiro

def setup_admins():
    admins = [
        {'email': 'luisotavio70p@gmail.com', 'username': 'lluisotaviosm', 'key': '3944346'},
        {'email': 'admin@monteiro.com', 'username': 'admin_monteiro', 'key': ''},
        {'email': 'admin@mineiro.com', 'username': 'admin_mineiro', 'key': ''},
    ]
    password = 'Monteiro03_'
    
    for admin_data in admins:
        email = admin_data['email']
        username = admin_data['username']
        bot_key = admin_data['key']
        
        if not CustomUser.objects.filter(email=email).exists():
            print(f"CRIANDO ADMIN: {email}...")
            user = CustomUser.objects.create_superuser(
                email=email,
                username=username,
                password=password,
                nome_completo='Luis Otavio (Dono/Barbeiro)',
                telefone='55281578065' 
            )
        else:
            print(f"ATUALIZANDO ADMIN: {email}...")
            user = CustomUser.objects.get(email=email)
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.set_password(password)
            user.save()
            
        # Garantir Perfil de Barbeiro com a Chave de API correta
        Barbeiro.objects.update_or_create(
            user=user, 
            defaults={
                'bio': 'Dono e Barbeiro' if email == 'luisotavio70p@gmail.com' else 'Administrador do Sistema',
                'whatsapp_bot_key': bot_key
            }
        )
        print(f"OK: {email} pronto. Bot Key: {bot_key if bot_key else 'N/A'}")

if __name__ == '__main__':
    setup_admins()
