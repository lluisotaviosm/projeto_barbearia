from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/cliente/', views.dashboard_cliente, name='dashboard_cliente'),
    path('dashboard/barbeiro/', views.dashboard_barbeiro, name='dashboard_barbeiro'),
    path('agendar/', views.agendar, name='agendar'),
    path('agendar/servicos/<int:barbeiro_id>/', views.selecionar_servico, name='selecionar_servico'),
    path('agendar/horario/<int:barbeiro_id>/<int:servico_id>/', views.selecionar_horario, name='selecionar_horario'),
    path('agendamento/confirmar/<int:agendamento_id>/', views.confirmar_agendamento, name='confirmar_agendamento'),
    path('agendamento/cancelar/<int:agendamento_id>/', views.cancelar_agendamento, name='cancelar_agendamento'),
    path('gestao/cadastrar-barbeiro/', views.cadastrar_barbeiro, name='cadastrar_barbeiro'),
    path('gestao/demitir-barbeiro/<int:barbeiro_id>/', views.demitir_barbeiro, name='demitir_barbeiro'),
    path('atendimento/finalizar/<int:agendamento_id>/', views.finalizar_atendimento, name='finalizar_atendimento'),
]
