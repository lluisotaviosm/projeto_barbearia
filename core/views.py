from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Barbeiro, Servico, Agendamento
from .forms import BarbeiroForm
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
import datetime

def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff or hasattr(request.user, 'perfil_barbeiro'):
            return redirect('dashboard_barbeiro')
        return redirect('dashboard_cliente')
    return render(request, 'home.html')

@login_required
def dashboard_cliente(request):
    agendamentos = Agendamento.objects.filter(cliente=request.user).order_by('-data', '-horario')
    return render(request, 'core/dashboard_cliente.html', {'agendamentos': agendamentos})

@login_required
def dashboard_barbeiro(request):
    if not request.user.is_staff and not hasattr(request.user, 'perfil_barbeiro'):
        messages.error(request, "Você não possui perfil de barbeiro.")
        return redirect('home')
    
    context = {}
    today = timezone.localdate()
    
    # Se for superuser, ele vê tudo consolidado
    if request.user.is_superuser:
        context['is_admin_only'] = not hasattr(request.user, 'perfil_barbeiro')
        context['barbeiros_lista'] = Barbeiro.objects.all()
        context['agendamentos_hoje'] = Agendamento.objects.filter(
            data=today
        ).order_by('barbeiro', 'horario')
        
        context['total_ganhos_geral'] = Agendamento.objects.filter(confirmado=True).aggregate(Sum('servico__preco'))['servico__preco__sum'] or 0
        context['total_clientes_geral'] = Agendamento.objects.values('cliente').distinct().count() or 0
        context['total_atendimentos_geral'] = Agendamento.objects.count()

    # Dados específicos se for um barbeiro
    if hasattr(request.user, 'perfil_barbeiro'):
        barbeiro = request.user.perfil_barbeiro
        context['barbeiro'] = barbeiro
        
        # Filtro de hoje para o barbeiro logado
        qs_hoje = Agendamento.objects.filter(barbeiro=barbeiro, data=today)
        
        if not request.user.is_superuser: # Se for apenas barbeiro, vê apenas o dele
            context['agendamentos_hoje'] = qs_hoje.order_by('horario')
        
        context['total_ganhos'] = Agendamento.objects.filter(barbeiro=barbeiro, confirmado=True).aggregate(Sum('servico__preco'))['servico__preco__sum'] or 0
        context['total_clientes'] = Agendamento.objects.filter(barbeiro=barbeiro).values('cliente').distinct().count() or 0
        context['total_atendimentos'] = Agendamento.objects.filter(barbeiro=barbeiro).count()
    
    context['today'] = today
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
        
        # Verificar se a hora já passou (se for hoje)
        try:
            from django.utils import timezone
            import datetime
            dt_agendamento = datetime.datetime.strptime(f"{data} {horario}", "%Y-%m-%d %H:%M")
            # Converte para datetime "aware" se necessário, ou compara com naive se timezone for naive
            # O Django geralmente usa aware se USE_TZ=True.
            dt_agendamento = timezone.make_aware(dt_agendamento)
            if dt_agendamento < timezone.now():
                messages.error(request, "Você não pode agendar um horário que já passou.")
                return render(request, 'core/selecionar_horario.html', {
                    'barbeiro': barbeiro, 'servico': servico, 'horarios': ["09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"]
                })
        except Exception as e:
            print(f"Erro na validação de data: {e}")

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
            
            # Notificação WhatsApp Automática (CallMeBot)
            if barbeiro.whatsapp_bot_key:
                try:
                    import re
                    import requests
                    bot_key = barbeiro.whatsapp_bot_key
                    # Limpar o telefone (deixar só números)
                    fone = re.sub(r'\D', '', barbeiro.user.telefone)
                    if fone and not fone.startswith('55'):
                        fone = f'55{fone}'
                    
                    cliente_nome = request.user.nome_completo or request.user.username
                    msg_bot = f"Novo Agendamento!%0ACliente: {cliente_nome}%0AServiço: {servico.nome}%0AData: {data}%0AHorário: {horario}"
                    url_bot = f"https://api.callmebot.com/whatsapp.php?phone={fone}&text={msg_bot}&apikey={bot_key}"
                    requests.get(url_bot, timeout=10)
                except Exception as e:
                    print(f"Erro ao enviar notificação bot: {e}")

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
    import urllib.parse
    import re
    
    agendamento = get_object_or_404(Agendamento, id=agendamento_id, cliente=request.user)
    
    # Gerar link WhatsApp
    mensagem = f"Olá, gostaria de confirmar meu agendamento na BARBEARIA DO MINEIRO JR.\n" \
               f"Serviço: {agendamento.servico.nome}\n" \
               f"Data: {agendamento.data.strftime('%d/%m/%Y')}\n" \
               f"Horário: {agendamento.horario.strftime('%H:%M')}"
    
    mensagem_encoded = urllib.parse.quote(mensagem)
    
    # Limpar o telefone do barbeiro
    fone_barbeiro = re.sub(r'\D', '', agendamento.barbeiro.user.telefone)
    if not fone_barbeiro.startswith('55'):
        fone_barbeiro = f"55{fone_barbeiro}"
        
    whatsapp_link = f"https://wa.me/{fone_barbeiro}?text={mensagem_encoded}"
    
    return render(request, 'core/confirmar_agendamento.html', {
        'agendamento': agendamento,
        'whatsapp_link': whatsapp_link
    })

@login_required
def cancelar_agendamento(request, agendamento_id):
    import urllib.parse
    import re
    
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    # Permite se for o barbeiro do agendamento OU se for superuser
    if request.user == agendamento.barbeiro.user or request.user.is_superuser:
        # Limpar o telefone (deixar só números)
        cliente_cel = re.sub(r'\D', '', agendamento.cliente.telefone)
        
        # Garantir o prefixo 55 se necessário
        if not cliente_cel.startswith('55'):
            cliente_cel = f"55{cliente_cel}"
            
        cliente_nome = agendamento.cliente.nome_completo if agendamento.cliente.nome_completo else agendamento.cliente.username
        
        mensagem = f"Olá {cliente_nome}, aqui é da BARBEARIA DO MINEIRO JR. Infelizmente precisamos reagendar seu horário de {agendamento.data.strftime('%d/%m/%Y')} às {agendamento.horario.strftime('%H:%M')}. Podemos conversar?"
        
        mensagem_encoded = urllib.parse.quote(mensagem)
        link_whatsapp = f"https://wa.me/{cliente_cel}?text={mensagem_encoded}"
        
        agendamento.delete()
        return redirect(link_whatsapp)
    
    messages.error(request, "Você não tem permissão para cancelar este agendamento.")
    return redirect('home')

@login_required
def cadastrar_barbeiro(request):
    if not request.user.is_superuser:
        messages.error(request, "Acesso restrito.")
        return redirect('home')
    
    if request.method == 'POST':
        form = BarbeiroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Barbeiro cadastrado com sucesso!")
            return redirect('dashboard_barbeiro')
    else:
        form = BarbeiroForm()
    
    return render(request, 'core/cadastrar_barbeiro.html', {'form': form})

@login_required
def finalizar_atendimento(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    
    # Apenas o barbeiro dono ou admin podem finalizar
    if request.user == agendamento.barbeiro.user or request.user.is_superuser:
        if request.method == 'POST':
            forma_pagamento = request.POST.get('forma_pagamento')
            agendamento.forma_pagamento = forma_pagamento
            agendamento.confirmado = True
            agendamento.status = 'CONCLUIDO'
            agendamento.save()
            messages.success(request, f"Atendimento de {agendamento.cliente.username} finalizado!")
            
    return redirect('dashboard_barbeiro')

@login_required
def demitir_barbeiro(request, barbeiro_id):
    if not request.user.is_superuser:
        messages.error(request, "Acesso restrito.")
        return redirect('home')
    
    try:
        barbeiro = Barbeiro.objects.get(id=barbeiro_id)
        user = barbeiro.user
        # Ao deletar o usuário, o Barbeiro é deletado por CASCADE (definido no modelo)
        user.delete() 
        messages.success(request, "Barbeiro removido com sucesso!")
    except Barbeiro.DoesNotExist:
        messages.warning(request, "Este barbeiro já foi removido.")
        
    return redirect('dashboard_barbeiro')
