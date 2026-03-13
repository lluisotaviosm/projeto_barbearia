import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from users.models import CustomUser

def check_users():
    print("--- LISTA DE USUARIOS NO BANCO ---")
    for user in CustomUser.objects.all():
        print(f"ID: {user.id} | Email: {user.email} | Staff: {user.is_staff} | Super: {user.is_superuser}")
    print("----------------------------------")

if __name__ == '__main__':
    check_users()
