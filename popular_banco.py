import os
import django
from decimal import Decimal
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smc.settings')
django.setup()

from django.contrib.auth.models import User
from cadastros.models import Colaborador, RegistroHora


def popular():
    print("Iniciando a carga de dados iniciais...")

    user_admin, _ = User.objects.get_or_create(username='admin')
    user_admin.set_password('admin123')
    user_admin.is_staff = True
    user_admin.is_superuser = True
    user_admin.first_name = "Administrador"
    user_admin.email = "admin@3neuron.com.br"
    user_admin.save()

    colab_admin, _ = Colaborador.objects.get_or_create(
        usuario=user_admin,
        defaults={
            'nome_completo': 'Carlos Silva (Gestor)',
            'cpf': '111.222.333-44',
            'email': 'admin@3neuron.com.br',
            'cargo': 'Gerente de Projetos',
            'tipo_contratacao': 'CLT',
            'perfil': 'ADM',
        }
    )
    print("-> Usuário Admin criado/atualizado: admin (senha: admin123)")

    user_consultor, _ = User.objects.get_or_create(username='consultor')
    user_consultor.set_password('consultor123')
    user_consultor.is_staff = False
    user_consultor.is_superuser = False
    user_consultor.first_name = "Consultor"
    user_consultor.email = "consultor@3neuron.com.br"
    user_consultor.save()

    colab_consultor, _ = Colaborador.objects.get_or_create(
        usuario=user_consultor,
        defaults={
            'nome_completo': 'Lucas Pereira (Consultor)',
            'cpf': '555.666.777-88',
            'email': 'consultor@3neuron.com.br',
            'cargo': 'Consultor de Sistemas Pleno',
            'tipo_contratacao': 'PJ',
            'perfil': 'CON',
        }
    )
    print("-> Usuário Consultor criado/atualizado: consultor (senha: consultor123)")

    user_mariana, _ = User.objects.get_or_create(username='mariana')
    user_mariana.set_password('mariana123')
    user_mariana.is_staff = False
    user_mariana.is_superuser = False
    user_mariana.email = 'mariana@3neuron.com.br'
    user_mariana.save()

    colab_estagio, _ = Colaborador.objects.get_or_create(
        cpf='999.888.777-66',
        defaults={
            'usuario': user_mariana,
            'nome_completo': 'Mariana Souza (Estagiária)',
            'email': 'mariana@3neuron.com.br',
            'cargo': 'Estagiária de Desenvolvimento',
            'tipo_contratacao': 'EST',
            'perfil': 'CON',
        }
    )
    if not colab_estagio.usuario:
        colab_estagio.usuario = user_mariana
        colab_estagio.save()
    print("-> Usuária Mariana criada/atualizada: mariana (senha: mariana123)")

    hoje = date.today()

    registros_teste = [
        {
            'colaborador': colab_consultor,
            'nome_projeto': 'Projeto Banco Alpha - Módulo Fiscal',
            'data': hoje - timedelta(days=2),
            'horas_trabalhadas': Decimal('8.0'),
            'descricao_atividade': 'Levantamento de requisitos e desenho do fluxo de conciliação fiscal.',
            'status': 'APR',
        },
        {
            'colaborador': colab_consultor,
            'nome_projeto': 'Projeto Banco Alpha - Módulo Fiscal',
            'data': hoje - timedelta(days=1),
            'horas_trabalhadas': Decimal('6.5'),
            'descricao_atividade': 'Implementação dos testes unitários das regras de emissão de relatórios.',
            'status': 'PEN',
        },
        {
            'colaborador': colab_consultor,
            'nome_projeto': 'Contrato Consultoria Logística Beta',
            'data': hoje,
            'horas_trabalhadas': Decimal('4.0'),
            'descricao_atividade': 'Reunião de alinhamento com clientes e homologação em ambiente de testes.',
            'status': 'AJU',
        },
        {
            'colaborador': colab_admin,
            'nome_projeto': 'Governança Interna 3Neuron',
            'data': hoje - timedelta(days=3),
            'horas_trabalhadas': Decimal('5.0'),
            'descricao_atividade': 'Planejamento estratégico trimestral e alocação de squads de consultoria.',
            'status': 'APR',
        },
    ]

    for reg_data in registros_teste:
        RegistroHora.objects.get_or_create(
            colaborador=reg_data['colaborador'],
            nome_projeto=reg_data['nome_projeto'],
            data=reg_data['data'],
            defaults=reg_data
        )

    print(f"-> {len(registros_teste)} registros de horas inseridos/verificados com sucesso!")
    print("\nBanco de dados preparado para apresentação!")


if __name__ == '__main__':
    popular()
