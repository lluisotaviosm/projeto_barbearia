import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from core.models import Barbeiro

def detailed_check():
    print("--- DETALHES DOS BARBEIROS ---")
    barbeiros = Barbeiro.objects.all()
    for b in barbeiros:
        print(f"ID: {b.id}")
        print(f"User Email: {b.user.email}")
        print(f"Bot Key: '{b.whatsapp_bot_key}'")
        print(f"Telefone no User: '{b.user.telefone}'")
        print("-" * 20)

if __name__ == '__main__':
    detailed_check()
