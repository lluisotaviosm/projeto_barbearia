from django.contrib import admin
from .models import Barbeiro, Servico, Agendamento

@admin.register(Barbeiro)
class BarbeiroAdmin(admin.ModelAdmin):
    pass

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'duracao_minutos']

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'barbeiro', 'servico', 'data', 'horario', 'confirmado']
    list_filter = ['data', 'barbeiro', 'confirmado']
