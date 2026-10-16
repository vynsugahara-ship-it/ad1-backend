from django.contrib import admin
from .models import Colaborador, RegistroHora


class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ["nome_completo", "cpf", "email", "cargo", "tipo_contratacao", "perfil"]
    list_filter = ["tipo_contratacao", "perfil"]
    ordering = ["nome_completo"]
    search_fields = ["nome_completo", "cpf"]
    actions_on_bottom = True


class RegistroHoraAdmin(admin.ModelAdmin):
    list_display = ["colaborador", "nome_projeto", "data", "horas_trabalhadas", "status"]
    list_filter = ["status", "nome_projeto", "data"]
    ordering = ["-data"]
    search_fields = ["nome_projeto", "descricao_atividade"]
    actions_on_bottom = True


admin.site.register(Colaborador, ColaboradorAdmin)
admin.site.register(RegistroHora, RegistroHoraAdmin)
