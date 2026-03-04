from django.db import models

class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    duracao_minutos = models.IntegerField(default=30)

    def __str__(self):
        return self.nome
