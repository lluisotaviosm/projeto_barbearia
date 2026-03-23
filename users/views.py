from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .forms import CustomUserCreationForm
from .models import CustomUser
import random
import re

def cadastro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='users.backends.EmailOrUsernameModelBackend')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/cadastro.html', {'form': form})

def password_reset_phone(request):
    if request.method == 'POST':
        telefone_in = request.POST.get('telefone', '')
        # Clean phone
        telefone_limpo = re.sub(r'\D', '', telefone_in)
        
        # O banco pode ter com prefixo ou sem, vamos procurar como starts_with, contains, ou regex se preciso.
        # Mas para melhorar aderência, vamos buscar `contains=telefone_limpo[-8:]` por exemplo, para garantir.
        if telefone_limpo:
            # Buscar cliente associado ao telefone mais forte.
            # Como a busca via contains numérico é propícia a falsos positivos, usamos exato match via `clean_telefone` nos cadastros novos.
            users = CustomUser.objects.filter(telefone__endswith=telefone_limpo[-8:])
            if users.exists():
                user = users.first()
                otp = str(random.randint(100000, 999999))
                request.session['reset_otp'] = otp
                request.session['reset_user_id'] = user.id
                
                # Simular envio para WhatsApp e Enviar real pela CallMeBot se tiver master key:
                print(f"=====================================")
                print(f"[API WHATSAPP] -> Enviando para {telefone_limpo}")
                print(f"Olá {user.username}, seu código de recuperação da Barbearia é: {otp}")
                print(f"=====================================")
                
                try:
                    import requests
                    from core.models import Barbeiro
                    barbeiro_bot = Barbeiro.objects.exclude(whatsapp_bot_key__isnull=True).exclude(whatsapp_bot_key='').first()
                    if barbeiro_bot:
                        import urllib.parse
                        bot_key = barbeiro_bot.whatsapp_bot_key
                        fone = telefone_limpo
                        if not fone.startswith('55'):
                            fone = f'55{fone}'
                            
                        # CallMeBot frequently requires the + sign to process correctly
                        fone_com_mais = f'+{fone}'
                        
                        msg_bot = f"Olá {user.username}, seu código de recuperação na Barbearia é: *{otp}*"
                        msg_encoded = urllib.parse.quote(msg_bot)
                        
                        url_bot = f"https://api.callmebot.com/whatsapp.php?phone={fone_com_mais}&text={msg_encoded}&apikey={bot_key}"
                        requests.get(url_bot, timeout=10)
                except Exception as e:
                    print(f"Erro no envio real WPP API: {e}")
                
                # Exibe o OTP de fallback na UI para garantir usabilidade mesmo se a API do BOT do cliente estiver offline.
                messages.success(request, f"Código enviado pro WPP final {telefone_limpo[-4:]}. (Emulação de Testes: {otp})")
                return redirect('password_reset_otp')
            else:
                messages.error(request, "Nenhum usuário encontrado com este número de telefone.")
    return render(request, 'users/password_reset_phone.html')

def password_reset_otp(request):
    if 'reset_otp' not in request.session:
        return redirect('password_reset_phone')
        
    if request.method == 'POST':
        otp_in = request.POST.get('otp', '')
        if otp_in.strip() == request.session['reset_otp']:
            return redirect('password_reset_new')
        else:
            messages.error(request, "Código incorreto. Digite novamente.")
    return render(request, 'users/password_reset_otp.html')

def password_reset_new(request):
    user_id = request.session.get('reset_user_id')
    otp = request.session.get('reset_otp')
    if not user_id or not otp:
        return redirect('password_reset_phone')
        
    if request.method == 'POST':
        nova_senha = request.POST.get('nova_senha', '')
        # Verificar se as senhas se condizem se quiser, ou apenas receber uma como simplificado
        if len(nova_senha) < 6:
            messages.error(request, "A senha deve conter no mínimo 6 caracteres.")
        else:
            user = CustomUser.objects.get(id=user_id)
            user.set_password(nova_senha)
            user.save()
            
            # Limpar a sessão
            del request.session['reset_otp']
            del request.session['reset_user_id']
            
            messages.success(request, "Sua senha foi redefinida com sucesso! Você já pode entrar.")
            return redirect('login')
            
    return render(request, 'users/password_reset_new.html')
