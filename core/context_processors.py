from django.conf import settings

def barbearia_config(request):
    return {
        'BARBERSHOP_NAME': getattr(settings, 'BARBERSHOP_NAME', 'Barbearia do Mineiro')
    }
