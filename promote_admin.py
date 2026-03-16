import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from users.models import CustomUser
from core.models import Barbeiro

def promote_user():
    email_part = 'luisotavio'
    users = CustomUser.objects.filter(email__icontains=email_part)
    if users.exists():
        for user in users:
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.save()
            Barbeiro.objects.get_or_create(
                user=user,
                defaults={'bio': 'Mestre Barbeiro Administrador'}
            )
            print(f"USUARIO {user.email} PROMOVIDO!")
    else:
        print("Nenhum usuario encontrado.")

if __name__ == '__main__':
    promote_user()
