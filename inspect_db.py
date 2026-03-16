import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from core.models import Agendamento, Barbeiro

def inspect_data():
    print(f"DEBUG: timezone.now(): {timezone.now()}")
    print(f"DEBUG: timezone.localdate(): {timezone.localdate()}")
    
    agendamentos = Agendamento.objects.all()
    print(f"\n--- TODOS OS AGENDAMENTOS ({agendamentos.count()}) ---")
    for a in agendamentos:
        print(f"ID: {a.id} | Cliente: {a.cliente.username} | Barbeiro: {a.barbeiro.user.username} | Data: {a.data} | Hora: {a.horario} | Confirmado: {a.confirmado}")
    
    print("\n--- BARBEIROS ---")
    for b in Barbeiro.objects.all():
        print(f"ID: {b.id} | User: {b.user.username} | Email: {b.user.email}")

if __name__ == '__main__':
    inspect_data()
