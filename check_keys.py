import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from core.models import Barbeiro

def check_bot_keys():
    print("--- CHAVES DE BOT CADASTRADAS ---")
    barbeiros = Barbeiro.objects.all()
    for b in barbeiros:
        print(f"Barbeiro: {b.user.username} | Email: {b.user.email} | API Key: {b.whatsapp_bot_key or 'VAZIA'}")
    print("--------------------------------")

if __name__ == '__main__':
    check_bot_keys()
