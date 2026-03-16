from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField('E-mail', unique=True)
    nome_completo = models.CharField('Nome Completo', max_length=255, blank=True, null=True)
    telefone = models.CharField('WhatsApp', max_length=20)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.nome_completo if self.nome_completo else self.username
