from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('barbeiro', 'Barbeiro'),
        ('cliente', 'Cliente'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='cliente')

    def is_barbeiro(self):
        return self.role == 'barbeiro'

    def is_cliente(self):
        return self.role == 'cliente'
