import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barbearia_prj.settings')
django.setup()

from usuarios.models import CustomUser
from core.models import Servico

def main():
    # 1. Transformar lluisotaviosm em Administrador, mas mantê-lo Cliente ou Barbeiro
    try:
        user = CustomUser.objects.get(username='lluisotaviosm')
        user.is_staff = True
        user.is_superuser = True
        user.save()
        print(f"Usuário {user.username} agora é um Administrador (pode acessar o /admin).")
    except CustomUser.DoesNotExist:
        pass

    # 1.5. Criar um barbeiro de demonstração (ou transformar o lluis em barbeiro)
    # Vamos criar um barbeiro novo chamado "Barbeiro_Joao"
    barbeiro, created = CustomUser.objects.get_or_create(
        username='barbeiro_joao',
        defaults={'email': 'joao@barbearia.com', 'role': 'barbeiro'}
    )
    if created:
        barbeiro.set_password('Barbearia123')
        barbeiro.save()
        print("Criado um barbeiro de exemplo: 'barbeiro_joao' com a senha 'Barbearia123'")

    # 2. Criar serviços básicos se não existirem
    servicos = [
        {"nome": "Corte Moderno", "descricao": "Corte de cabelo com tesoura e máquina, fade ou social.", "preco": 45.00, "duracao_minutos": 45},
        {"nome": "Barba Terapia", "descricao": "Corte de barba com toalha quente e massagem facial.", "preco": 35.00, "duracao_minutos": 30},
        {"nome": "Combo Corte + Barba", "descricao": "Pacote completo com desconto especial para corte e barba.", "preco": 70.00, "duracao_minutos": 75},
        {"nome": "Sobrancelha", "descricao": "Alinhamento e corte de sobrancelha.", "preco": 15.00, "duracao_minutos": 15},
    ]

    for s in servicos:
        obj, created = Servico.objects.get_or_create(
            nome=s['nome'],
            defaults={
                'descricao': s['descricao'],
                'preco': s['preco'],
                'duracao_minutos': s['duracao_minutos'],
            }
        )
        if created:
            print(f"Serviço '{s['nome']}' criado com sucesso.")
            
if __name__ == '__main__':
    main()
