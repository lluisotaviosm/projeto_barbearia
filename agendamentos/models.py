from django.db import models
from usuarios.models import CustomUser
from core.models import Servico

class Agendamento(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    )
    cliente = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='agendamentos_cliente')
    barbeiro = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='agendamentos_barbeiro', null=True, blank=True)
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    data_hora = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')

    class Meta:
        ordering = ['-data_hora']

    def __str__(self):
        return f"{self.cliente.username} - {self.servico.nome} em {self.data_hora.strftime('%d/%m/%Y %H:%M')}"
