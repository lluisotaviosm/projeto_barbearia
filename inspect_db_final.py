import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from users.models import CustomUser
from core.models import Barbeiro

def detailed_inspection():
    print("--- INSPEÇÃO DE USUÁRIOS ---")
    users = CustomUser.objects.all()
    for u in users:
        has_profile = hasattr(u, 'perfil_barbeiro')
        profile_key = u.perfil_barbeiro.whatsapp_bot_key if has_profile else 'N/A'
        print(f"Email: {u.email} | Username: {u.username} | Staff: {u.is_staff} | Super: {u.is_superuser} | Barbeiro: {has_profile} | Bot Key: {profile_key} | Telefone: {u.telefone}")
    
    print("\n--- BARBEIROS (Model) ---")
    barbeiros = Barbeiro.objects.all()
    for b in barbeiros:
        print(f"ID: {b.id} | User: {b.user.email} | Key: {b.whatsapp_bot_key}")

if __name__ == '__main__':
    detailed_inspection()
