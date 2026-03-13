import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from users.models import CustomUser
from core.models import Barbeiro

def promote_user():
    email = 'luisotavio70p@gmail.com'
    try:
        user = CustomUser.objects.get(email=email)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        
        # Criar perfil de barbeiro se não existir
        Barbeiro.objects.get_or_create(
            user=user,
            defaults={
                'bio': 'Mestre Barbeiro e Administrador',
                'whatsapp_bot_key': ''
            }
        )
        print(f"USUARIO {email} PROMOVIDO A ADMIN E BARBEIRO COM SUCESSO!")
    except CustomUser.DoesNotExist:
        print(f"ERRO: Usuario {email} nao encontrado no banco de dados.")

if __name__ == '__main__':
    promote_user()
