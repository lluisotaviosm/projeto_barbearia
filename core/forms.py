from django import forms
from .models import Barbeiro
from django.contrib.auth import get_user_model

User = get_user_model()

class BarbeiroForm(forms.ModelForm):
    email = forms.EmailField(label='E-mail do Barbeiro')
    username = forms.CharField(label='Nome de Usuário')
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    nome_completo = forms.CharField(label='Nome Completo', required=False)
    telefone = forms.CharField(label='Telefone (WhatsApp)')

    class Meta:
        model = Barbeiro
        fields = ['foto', 'bio', 'whatsapp_bot_key']

    def save(self, commit=True):
        user = User.objects.create_user(
            email=self.cleaned_data['email'],
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            nome_completo=self.cleaned_data.get('nome_completo', ''),
            telefone=self.cleaned_data['telefone']
        )
        barbeiro = super().save(commit=False)
        barbeiro.user = user
        if commit:
            barbeiro.save()
        return barbeiro
