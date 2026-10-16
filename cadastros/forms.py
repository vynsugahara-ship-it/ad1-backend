from django import forms
from django.contrib.auth.models import User
from .models import Colaborador, RegistroHora


class ColaboradorForm(forms.ModelForm):
    nome_usuario = forms.CharField(
        label="Nome de Usuário (Login)",
        max_length=150,
        help_text="Identificador para entrar no sistema."
    )
    senha = forms.CharField(
        label="Senha de Acesso",
        widget=forms.PasswordInput,
        required=False,
        help_text="Defina a senha inicial (na edição, deixe em branco para manter a atual)."
    )

    class Meta:
        model = Colaborador
        fields = [
            'nome_completo',
            'cpf',
            'email',
            'cargo',
            'tipo_contratacao',
            'perfil',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.usuario:
            self.fields['nome_usuario'].initial = self.instance.usuario.username
        else:
            self.fields['senha'].required = True

    def clean_nome_usuario(self):
        nome_usuario = self.cleaned_data.get('nome_usuario')
        usuario_atual = self.instance.usuario if (self.instance and self.instance.pk) else None

        qs = User.objects.filter(username=nome_usuario)
        if usuario_atual:
            qs = qs.exclude(pk=usuario_atual.pk)
        if qs.exists():
            raise forms.ValidationError("Este nome de usuário já está em uso. Escolha outro.")
        return nome_usuario

    def save(self, commit=True):
        colaborador = super().save(commit=False)
        nome_usuario = self.cleaned_data.get('nome_usuario')
        senha = self.cleaned_data.get('senha')
        is_admin = (colaborador.perfil == 'ADM')

        if colaborador.usuario:
            usuario = colaborador.usuario
            usuario.username = nome_usuario
            if senha:
                usuario.set_password(senha)
            usuario.is_staff = is_admin
            usuario.is_superuser = is_admin
            usuario.email = colaborador.email
            usuario.save()
        else:
            usuario = User.objects.create_user(
                username=nome_usuario,
                password=senha,
                email=colaborador.email,
                is_staff=is_admin,
                is_superuser=is_admin
            )
            colaborador.usuario = usuario

        if commit:
            colaborador.save()
        return colaborador


class RegistroHoraForm(forms.ModelForm):
    class Meta:
        model = RegistroHora
        fields = [
            'colaborador',
            'nome_projeto',
            'data',
            'horas_trabalhadas',
            'descricao_atividade',
            'status',
        ]
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and not user.is_staff:
            colab = Colaborador.objects.filter(usuario=user).first()
            if colab:
                self.fields['colaborador'].queryset = Colaborador.objects.filter(pk=colab.pk)
                self.fields['colaborador'].initial = colab
                self.fields['colaborador'].disabled = True

            self.fields['status'].initial = 'PEN'
            self.fields['status'].disabled = True
