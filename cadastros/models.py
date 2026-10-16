from django.db import models
from django.contrib.auth.models import User


class Colaborador(models.Model):
    TIPOS_CONTRATACAO = {
        "CLT": "CLT",
        "EST": "Estagiário",
        "PJ": "Pessoa Jurídica (PJ)",
    }
    PERFIS = {
        "CON": "Consultor (Funcionário)",
        "ADM": "Administrativo (Admin)",
    }

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="usuário do sistema",
        null=True,
        blank=True
    )
    nome_completo = models.CharField("nome completo", max_length=100)
    cpf = models.CharField("CPF", max_length=14)
    email = models.EmailField("e-mail")
    cargo = models.CharField("cargo", max_length=50)
    tipo_contratacao = models.CharField("tipo de contratação", max_length=3, choices=TIPOS_CONTRATACAO)
    perfil = models.CharField("perfil de acesso", max_length=3, choices=PERFIS, default="CON")

    def __str__(self):
        return self.nome_completo


class RegistroHora(models.Model):
    STATUS_APROVACAO = {
        "PEN": "Pendente",
        "APR": "Aprovado",
        "AJU": "Solicitado Ajuste",
    }

    colaborador = models.ForeignKey(
        Colaborador,
        on_delete=models.CASCADE,
        verbose_name="colaborador"
    )
    nome_projeto = models.CharField("nome do projeto/contrato", max_length=100)
    data = models.DateField("data da atividade")
    horas_trabalhadas = models.DecimalField("quantidade de horas", max_digits=4, decimal_places=1)
    descricao_atividade = models.TextField("descrição da atividade realizada")
    status = models.CharField("status de aprovação", max_length=3, choices=STATUS_APROVACAO, default="PEN")

    def __str__(self):
        return f"{self.colaborador.nome_completo} - {self.nome_projeto} ({self.data})"
