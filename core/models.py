from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Barbeiro(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil_barbeiro')
    foto = models.ImageField(upload_to='barbeiros/', null=True, blank=True)
    bio = models.TextField(blank=True)
    whatsapp_bot_key = models.CharField('Chave Bot WhatsApp', max_length=255, blank=True, null=True)

    def __str__(self):
        nome = self.user.nome_completo if self.user.nome_completo else self.user.username
        return nome

class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    duracao_minutos = models.IntegerField(default=30)
    imagem = models.ImageField(upload_to='servicos/', null=True, blank=True)

    def __str__(self):
        return self.nome

class Agendamento(models.Model):
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='agendamentos')
    barbeiro = models.ForeignKey(Barbeiro, on_delete=models.CASCADE, related_name='agenda')
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    data = models.DateField()
    horario = models.TimeField()
    status = models.CharField(max_length=20, default='PENDENTE')
    forma_pagamento = models.CharField(max_length=50, blank=True, null=True)
    confirmado = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('barbeiro', 'data', 'horario')
        ordering = ['data', 'horario']

    def clean(self):
        # Validação extra para evitar duplicidade manual se unique_together falhar no formulário
        if Agendamento.objects.filter(barbeiro=self.barbeiro, data=self.data, horario=self.horario).exclude(pk=self.pk).exists():
            raise ValidationError('Este barbeiro já possui um agendamento neste horário.')

    def __str__(self):
        cliente_nome = self.cliente.nome_completo if self.cliente.nome_completo else self.cliente.username
        return f"{cliente_nome} - {self.barbeiro} - {self.data} {self.horario}"
