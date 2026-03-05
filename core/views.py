from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django import forms
from datetime import datetime

# Imports dos seus Apps
from core.models import Servico
from agendamentos.models import Agendamento
from usuarios.models import CustomUser

# --- FORMULÁRIOS ---

class ClienteCadastroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email',)

# --- VIEWS PÚBLICAS ---

def index(request):
    servicos = Servico.objects.all()
    return render(request, 'core/index.html', {'servicos': servicos})

def cadastro_cliente(request):
    if request.method == 'POST':
        form = ClienteCadastroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'cliente'
            user.save()
            messages.success(request, f'Conta criada com sucesso, {user.username}! Faça seu login.')
            return redirect('account_login') # URL padrão do Allauth
        else:
            # Essencial para você ver o erro no Log do Railway!
            print(f"ERRO NO CADASTRO: {form.errors}")
            messages.error(request, 'Erro ao criar conta. Verifique se a senha é forte ou se o usuário já existe.')
    else:
        form = ClienteCadastroForm()
    return render(request, 'core/cadastro_cliente.html', {'form': form})

# --- VIEWS PROTEGIDAS (CLIENTE) ---

@login_required
def dashboard_cliente(request):
    if not request.user.is_cliente():
        if request.user.is_barbeiro():
             return redirect('dashboard_barbeiro')
        return render(request, 'core/acesso_negado.html')
        
    meus_agendamentos = Agendamento.objects.filter(cliente=request.user).order_by('data_hora')
    return render(request, 'core/dashboard_cliente.html', {'agendamentos': meus_agendamentos})

@login_required
def novo_agendamento(request):
    if request.user.is_barbeiro():
        return redirect('dashboard_barbeiro')

    servicos = Servico.objects.all()
    barbeiros = CustomUser.objects.filter(role='barbeiro')

    if request.method == 'POST':
        servico_id = request.POST.get('servico_id')
        barbeiro_id = request.POST.get('barbeiro_id')
        data_hora_str = request.POST.get('data_hora')
        
        if servico_id and barbeiro_id and data_hora_str:
            try:
                data_hora = timezone.make_aware(datetime.strptime(data_hora_str, '%Y-%m-%dT%H:%M'))
                
                if data_hora < timezone.now():
                    messages.error(request, 'Não é possível agendar em um horário no passado.')
                    return redirect('novo_agendamento')

                hora_agendamento = data_hora.hour
                if hora_agendamento < 9 or hora_agendamento >= 18:
                    messages.error(request, 'Expediente: 09:00 às 18:00.')
                    return redirect('novo_agendamento')

                conflito = Agendamento.objects.filter(
                    barbeiro_id=barbeiro_id, 
                    data_hora=data_hora,
                    status__in=['pendente', 'concluido']
                ).exists()

                if conflito:
                    messages.error(request, 'Este horário já está reservado.')
                    return redirect('novo_agendamento')
                
                Agendamento.objects.create(
                    cliente=request.user,
                    barbeiro_id=barbeiro_id,
                    servico_id=servico_id,
                    data_hora=data_hora,
                    status='pendente'
                )
                
                messages.success(request, 'Agendamento realizado com sucesso!')
                return redirect('dashboard_cliente')
                
            except ValueError:
                 messages.error(request, 'Formato de data inválido.')

    return render(request, 'core/novo_agendamento.html', {'servicos': servicos, 'barbeiros': barbeiros})

# --- VIEWS PROTEGIDAS (BARBEIRO / GESTOR) ---

@login_required
def dashboard_barbeiro(request):
    if not request.user.is_barbeiro() and not request.user.is_superuser:
        return render(request, 'core/acesso_negado.html')
    
    agendamentos = Agendamento.objects.filter(barbeiro=request.user).order_by('data_hora')
    total_mes = agendamentos.filter(status='concluido').aggregate(Sum('servico__preco'))['servico__preco__sum'] or 0
    hoje = timezone.now().date()
    agendamentos_hoje = agendamentos.filter(data_hora__date=hoje)
    
    context = {
        'agendamentos': agendamentos,
        'agendamentos_hoje': agendamentos_hoje,
        'total_mes': total_mes
    }
    return render(request, 'core/dashboard_barbeiro.html', context)

@login_required
def dashboard_gestor(request):
    if not request.user.is_superuser:
        return render(request, 'core/acesso_negado.html')
        
    agendamentos_concluidos = Agendamento.objects.filter(status='concluido')
    receita_total = agendamentos_concluidos.aggregate(Sum('servico__preco'))['servico__preco__sum'] or 0
    proximos_agendamentos = Agendamento.objects.filter(data_hora__gte=timezone.now()).order_by('data_hora')[:15]
    barbeiros = CustomUser.objects.filter(role='barbeiro')
    
    if request.method == 'POST':
        novo_username = request.POST.get('username')
        novo_email = request.POST.get('email')
        nova_senha = request.POST.get('password')
        
        if novo_username and novo_email and nova_senha:
            if CustomUser.objects.filter(username=novo_username).exists():
                messages.error(request, 'Username em uso.')
            else:
                CustomUser.objects.create_user(
                    username=novo_username, email=novo_email, password=nova_senha, role='barbeiro'
                )
                messages.success(request, f'Barbeiro {novo_username} cadastrado!')
                return redirect('dashboard_gestor')
                
    return render(request, 'core/dashboard_gestor.html', {
        'receita_total': receita_total,
        'proximos_agendamentos': proximos_agendamentos,
        'barbeiros': barbeiros,
        'agendamentos_concluidos': agendamentos_concluidos.count()
    })

@login_required
def cancelar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    if request.user == agendamento.cliente or request.user.is_superuser:
        agendamento.delete()
        messages.success(request, 'Agendamento cancelado.')
    else:
        messages.error(request, 'Sem permissão.')
    return redirect('dashboard_cliente')

@login_required
def excluir_barbeiro(request, barbeiro_id):
    if not request.user.is_superuser:
        return redirect('index')
    barbeiro = get_object_or_404(CustomUser, id=barbeiro_id, role='barbeiro')
    barbeiro.delete()
    messages.success(request, 'Barbeiro removido.')
    return redirect('dashboard_gestor')
