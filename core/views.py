from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Servico
from agendamentos.models import Agendamento
from usuarios.models import CustomUser
from django.db.models import Sum
from datetime import datetime
from django.utils import timezone
from django.contrib import messages

def index(request):
    servicos = Servico.objects.all()
    return render(request, 'core/index.html', {'servicos': servicos})

@login_required
def dashboard_barbeiro(request):
    if not request.user.is_barbeiro() and not request.user.is_superuser:
        return render(request, 'core/acesso_negado.html')
    
    agendamentos = Agendamento.objects.filter(barbeiro=request.user).order_by('data_hora')
    
    # Total de ganhos no mes (agendamentos concluidos do barbeiro atual)
    total_mes = agendamentos.filter(status='concluido').aggregate(Sum('servico__preco'))['servico__preco__sum'] or 0
    
    # Agendamentos de hoje
    hoje = timezone.now().date()
    agendamentos_hoje = agendamentos.filter(data_hora__date=hoje)
    
    context = {
        'agendamentos': agendamentos,
        'agendamentos_hoje': agendamentos_hoje,
        'total_mes': total_mes
    }
    
    return render(request, 'core/dashboard_barbeiro.html', context)

@login_required
def dashboard_cliente(request):
    # Força a ser cliente para acessar essa view
    if not request.user.is_cliente():
        # Se um barbeiro clicar em 'Sou Cliente' por engano, redireciona pro painel dele
        if request.user.is_barbeiro():
             return redirect('dashboard_barbeiro')
        return render(request, 'core/acesso_negado.html')
        
    meus_agendamentos = Agendamento.objects.filter(cliente=request.user).order_by('data_hora')
    return render(request, 'core/dashboard_cliente.html', {'agendamentos': meus_agendamentos})

@login_required
def novo_agendamento(request):
    if request.user.is_barbeiro():
        # Barbeiros marcando horário? Melhor não.
        return redirect('dashboard_barbeiro')

    servicos = Servico.objects.all()
    barbeiros = CustomUser.objects.filter(role='barbeiro')

    if request.method == 'POST':
        servico_id = request.POST.get('servico_id')
        barbeiro_id = request.POST.get('barbeiro_id')
        data_hora_str = request.POST.get('data_hora')
        
        if servico_id and barbeiro_id and data_hora_str:
            try:
                # Converter de 'YYYY-MM-DDTHH:MM' para timezone-aware datetime
                data_hora = timezone.make_aware(datetime.strptime(data_hora_str, '%Y-%m-%dT%H:%M'))
                
                # Regra: não pode marcar no passado
                if data_hora < timezone.now():
                    messages.error(request, 'Não é possível agendar em um horário no passado.')
                    return redirect('novo_agendamento')
                # Checar expediente (9h às 18h)
                hora_agendamento = data_hora.hour
                if hora_agendamento < 9 or hora_agendamento >= 18:
                    messages.error(request, 'O agendamento deve ser feito durante o horário de expediente, entre 09:00 e 18:00.')
                    return redirect('novo_agendamento')

                # Checar se o barbeiro já tem agendamento na mesma hora
                conflito = Agendamento.objects.filter(
                    barbeiro_id=barbeiro_id, 
                    data_hora=data_hora,
                    status__in=['pendente', 'concluido']
                ).exists()

                if conflito:
                    messages.error(request, 'Este horário já está reservado com este barbeiro.')
                    return redirect('novo_agendamento')
                
                # Criar agendamento
                Agendamento.objects.create(
                    cliente=request.user,
                    barbeiro_id=barbeiro_id,
                    servico_id=servico_id,
                    data_hora=data_hora,
                    status='pendente'
                )
                
                barbeiro_nome = CustomUser.objects.get(id=barbeiro_id).username.title()
                data_formatada = data_hora.strftime("%d/%m/%Y")
                hora_formatada = data_hora.strftime("%H:%M")
                
                messages.success(request, f'Parabéns {request.user.username.title()}! Você agendou para o dia {data_formatada}, na hora {hora_formatada} com o barbeiro {barbeiro_nome}. Esperamos você lá!')
                return redirect('dashboard_cliente')
                
            except ValueError:
                 messages.error(request, 'Formato de data inválido.')

    return render(request, 'core/novo_agendamento.html', {'servicos': servicos, 'barbeiros': barbeiros})

@login_required
def dashboard_gestor(request):
    # Apenas superusers (donos) podem acessar o painel gestor
    if not request.user.is_superuser:
        return render(request, 'core/acesso_negado.html')
        
    # Saldo total da barbearia (todos os barbeiros)
    agendamentos_concluidos = Agendamento.objects.filter(status='concluido')
    receita_total = agendamentos_concluidos.aggregate(Sum('servico__preco'))['servico__preco__sum'] or 0
    
    # Listagem de próximos agendamentos globais (qualquer barbeiro)
    proximos_agendamentos = Agendamento.objects.filter(data_hora__gte=timezone.now()).order_by('data_hora')[:15]
    
    # Lista de todos os barbeiros
    barbeiros = CustomUser.objects.filter(role='barbeiro')
    
    # Lógica para cadastrar novo barbeiro
    if request.method == 'POST':
        novo_username = request.POST.get('username')
        novo_email = request.POST.get('email')
        nova_senha = request.POST.get('password')
        
        if novo_username and novo_email and nova_senha:
            if CustomUser.objects.filter(username=novo_username).exists():
                messages.error(request, 'Este nome de usuário já está em uso.')
            elif CustomUser.objects.filter(email=novo_email).exists():
                 messages.error(request, 'Este e-mail já está sendo usado por outro barbeiro.')
            else:
                novo_barbeiro = CustomUser.objects.create_user(
                    username=novo_username,
                    email=novo_email,
                    password=nova_senha,
                    role='barbeiro'
                )
                messages.success(request, f'Barbeiro {novo_barbeiro.username} cadastrado com sucesso!')
                return redirect('dashboard_gestor')
                
    context = {
        'receita_total': receita_total,
        'proximos_agendamentos': proximos_agendamentos,
        'barbeiros': barbeiros,
        'agendamentos_concluidos': agendamentos_concluidos.count()
    }
    
    return render(request, 'core/dashboard_gestor.html', context)


@login_required
def cancelar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    # Apenas o dono do agendamento ou o gestor podem cancelar
    if request.user == agendamento.cliente or request.user.is_superuser:
        agendamento.delete()
        messages.success(request, 'Agendamento cancelado com sucesso.')
    else:
        messages.error(request, 'Você não tem permissão para cancelar este agendamento.')
        
    return redirect('dashboard_cliente')


@login_required
def excluir_barbeiro(request, barbeiro_id):
    # Apenas superuser pode excluir barbeiro
    if not request.user.is_superuser:
        messages.error(request, 'Acesso Negado.')
        return redirect('index')
        
    barbeiro = get_object_or_404(CustomUser, id=barbeiro_id, role='barbeiro')
    
    # Opcional: checar se ele tem agendamentos pendentes antes de excluir, mas por hora vamos forçar.
    nome = barbeiro.username
    barbeiro.delete()
    messages.success(request, f'O barbeiro {nome} foi removido da equipe.')
    
    return redirect('dashboard_gestor')
