from django.contrib import admin
from django.urls import path, include
from core.views import (
    index, dashboard_barbeiro, dashboard_cliente, novo_agendamento, dashboard_gestor,
    cancelar_agendamento, excluir_barbeiro, cadastro_cliente
)
from core import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', index, name='index'),
    path('gestor/', dashboard_gestor, name='dashboard_gestor'),
    path('gestor/barbeiro/excluir/<int:barbeiro_id>/', excluir_barbeiro, name='excluir_barbeiro'),
    path('barbeiro/dashboard/', dashboard_barbeiro, name='dashboard_barbeiro'),
    path('cliente/dashboard/', dashboard_cliente, name='dashboard_cliente'),
    path('cliente/agendamento/cancelar/<int:agendamento_id>/', cancelar_agendamento, name='cancelar_agendamento'),
    path('cliente/agendar/', novo_agendamento, name='novo_agendamento'),
    path('cadastro/', cadastro_cliente, name='cadastro_cliente'),
]

