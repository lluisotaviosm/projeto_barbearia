from django.shortcuts import render, redirect, get_object_or_优质的
from django.contrib.auth.decorators import login_required
from .models import Barbeiro, Servico, Agendamento
from django.contrib import messages
from django.db.models import Sum, Count
import datetime

def home(request):
    return render(request, 'home.html')

@login_required
def dashboard_cliente(request):
    agendamentos = Agendamento.objects.filter(cliente=request.user).order_by('-data', '-horario')
    return render(request, 'core/dashboard_cliente.html', {'agendamentos': agendamentos})

@login_required
def dashboard_barbeiro(request):
    try:
        barbeiro = request.user.perfil_barbeiro
    except Barbeiro.DoesNotExist:
        messages.error(request, "Você não possui perfil de barbeiro.")
        return redirect('home')
    
    agendamentos_hoje = Agendamento.objects.filter(
        barbeiro=barbeiro, 
        data=datetime.date.today()
    ).order_by('horario')
    
    total_ganhos = Agendamento.objects.filter(barbeiro=barbeiro, confirmado=True).aggregate(Sum('servico__preco'))['servico__preco__sum'] or 0
    total_clientes = Agendamento.objects.filter(barbeiro=barbeiro).values('cliente').distinct().count() or 0
    total_atendimentos = Agendamento.objects.filter(barbeiro=barbeiro).count()
    
    context = {
        'barbeiro': barbeiro,
        'agendamentos_hoje': agendamentos_hoje,
        'total_ganhos': total_ganhos,
        'total_clientes': total_clientes,
        'total_atendimentos': total_atendimentos,
    }
    return render(request, 'core/dashboard_barbeiro.html', context)

@login_required
def agendar(request):
    barbeiros = Barbeiro.objects.all()
    return render(request, 'core/selecionar_barbeiro.html', {'barbeiros': barbeiros})

@login_required
def selecionar_servico(request, barbeiro_id):
    barbeiro = get_object_or_404(Barbeiro, id=barbeiro_id)
    servicos = Servico.objects.all()
    return render(request, 'core/selecionar_servico.html', {'barbeiro': barbeiro, 'servicos': servicos})

@login_required
def selecionar_horario(request, barbeiro_id, servico_id):
    barbeiro = get_object_or_404(Barbeiro, id=barbeiro_id)
    servico = get_object_or_404(Servico, id=servico_id)
    
    if request.method == 'POST':
        data = request.POST.get('data')
        horario = request.POST.get('horario')
        
        # Verificar duplicidade
        if Agendamento.objects.filter(barbeiro=barbeiro, data=data, horario=horario).exists():
            messages.error(request, "Este horário já está ocupado.")
        else:
            agendamento = Agendamento.objects.create(
                cliente=request.user,
                barbeiro=barbeiro,
                servico=servico,
                data=data,
                horario=horario
            )
            messages.success(request, "Agendamento realizado com sucesso!")
            # Simulação de Notificação WhatsApp
            return redirect('confirmar_agendamento', agendamento_id=agendamento.id)
            
    # Horários fixos para exemplo
    horarios = ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
    return render(request, 'core/selecionar_horario.html', {
        'barbeiro': barbeiro, 
        'servico': servico,
        'horarios': horarios
    })

@login_required
def confirmar_agendamento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id, cliente=request.user)
    
    # Gerar link WhatsApp
    mensagem = f"Olá, gostaria de confirmar meu agendamento na Barbearia do Mineiro.%0A" \
               f"Serviço: {agendamento.servico.nome}%0A" \
               f"Data: {agendamento.data}%0A" \
               f"Horário: {agendamento.horario}"
    
    whatsapp_link = f"https://wa.me/55{agendamento.barbeiro.user.telefone}?text={mensagem}"
    
    return render(request, 'core/confirmar_agendamento.html', {
        'agendamento': agendamento,
        'whatsapp_link': whatsapp_link
    })

@login_required
def cancelar_agendamento(request, agendamento_id):
    # Barbeiro cancelando
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    if request.user == agendamento.barbeiro.user:
        cliente_cel = agendamento.cliente.telefone
        mensagem = f"Olá {agendamento.cliente.nome_completo}, infelizmente precisamos reagendar seu horário de {agendamento.data} às {agendamento.horario}. Podemos conversar?"
        link_cancelamento = f"https://wa.me/55{cliente_cel}?text={mensagem.replace(' ', '%20')}"
        agendamento.delete()
        return redirect(link_cancelamento)
    
    return redirect('home')
