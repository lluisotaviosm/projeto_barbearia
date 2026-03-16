import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from users.models import CustomUser
from core.models import Barbeiro

def setup_final_clean():
    # 1. admin@monteiro.com AS OWNER
    admin_mon, _ = CustomUser.objects.update_or_create(
        email='admin@monteiro.com',
        defaults={
            'username': 'admin_monteiro',
            'is_superuser': True,
            'is_staff': True,
            'is_active': True,
            'nome_completo': 'Luis Otavio (Dono)'
        }
    )
    admin_mon.set_password('Monteiro03_')
    admin_mon.save()

    # 2. luisotavio70p@gmail.com AS OFFICIAL BARBER (is_staff=True)
    barber_user, _ = CustomUser.objects.update_or_create(
        email='luisotavio70p@gmail.com',
        defaults={
            'username': 'lluisotaviosm',
            'is_superuser': False,
            'is_staff': True,
            'is_active': True,
            'telefone': '55281578065',
            'nome_completo': 'Luis Otavio (Barbeiro)'
        }
    )
    barber_user.set_password('Monteiro03_')
    barber_user.save()

    # 3. LINK BOT KEY (3944346)
    Barbeiro.objects.update_or_create(
        user=barber_user,
        defaults={
            'bio': 'Barbeiro Oficial',
            'whatsapp_bot_key': '3944346'
        }
    )

    # 4. REMOVE OTHERS
    CustomUser.objects.filter(email='admin@mineiro.com').delete()
    Barbeiro.objects.filter(user=admin_mon).update(whatsapp_bot_key='')

    print(f"DONE: {admin_mon.email} is Owner. {barber_user.email} is Barber with Bot.")

if __name__ == '__main__':
    setup_final_clean()
