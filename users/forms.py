from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(),
        min_length=6
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'telefone')
        labels = {
            'username': 'Nome de Usuário',
            'telefone': 'WhatsApp',
        }

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone', '')
        import re
        return re.sub(r'\D', '', telefone)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        # Generates a dummy email required by the CustomUser model schema
        user.email = f"{user.username}@cliente.barbearia.local"
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('email', 'username', 'telefone')

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone', '')
        import re
        return re.sub(r'\D', '', telefone)
