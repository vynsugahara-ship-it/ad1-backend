from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Colaborador, RegistroHora
from .forms import ColaboradorForm, RegistroHoraForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    mensagem_erro = None
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            usuario = form.get_user()
            login(request, usuario)
            messages.success(request, f"Bem-vindo(a), {usuario.username}!")
            return redirect('home')
        else:
            mensagem_erro = "Usuário ou senha inválidos. Tente novamente."
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {
        'form': form,
        'mensagem_erro': mensagem_erro
    })


def logout_view(request):
    logout(request)
    messages.info(request, "Sessão encerrada com sucesso.")
    return redirect('login')


@login_required
def home(request):
    if request.user.is_staff:
        total_colaboradores = Colaborador.objects.count()
        total_registros = RegistroHora.objects.count()
        total_horas_geral = sum(r.horas_trabalhadas for r in RegistroHora.objects.all())
        total_pendentes = RegistroHora.objects.filter(status='PEN').count()

        contexto = {
            'total_colaboradores': total_colaboradores,
            'total_registros': total_registros,
            'total_horas_geral': total_horas_geral,
            'total_pendentes': total_pendentes,
        }
    else:
        colaborador = Colaborador.objects.filter(usuario=request.user).first()
        minhas_horas_regs = RegistroHora.objects.filter(colaborador=colaborador) if colaborador else []
        total_minhas_horas = sum(r.horas_trabalhadas for r in minhas_horas_regs)
        minhas_pendentes = sum(1 for r in minhas_horas_regs if r.status == 'PEN')
        minhas_aprovadas = sum(1 for r in minhas_horas_regs if r.status == 'APR')

        contexto = {
            'colaborador': colaborador,
            'total_minhas_horas': total_minhas_horas,
            'minhas_pendentes': minhas_pendentes,
            'minhas_aprovadas': minhas_aprovadas,
        }

    return render(request, 'home.html', contexto)


@login_required
def lista_colaboradores(request):
    colaboradores = list(Colaborador.objects.all().order_by('nome_completo'))
    for colab in colaboradores:
        colab.total_horas_acumuladas = sum(r.horas_trabalhadas for r in colab.registrohora_set.all())

    return render(request, 'lista_colaboradores.html', {
        'colaboradores': colaboradores
    })


@login_required
def cadastrar_colaborador(request):
    if not request.user.is_staff:
        messages.error(request, "Apenas administradores podem cadastrar colaboradores.")
        return redirect('lista_colaboradores')

    if request.method == 'POST':
        form = ColaboradorForm(request.POST)
        if form.is_valid():
            colab = form.save()
            messages.success(request, f"Colaborador {colab.nome_completo} cadastrado com sucesso!")
            return redirect('lista_colaboradores')
    else:
        form = ColaboradorForm()

    return render(request, 'form_colaborador.html', {
        'form': form,
        'titulo': 'Cadastrar Novo Colaborador'
    })


@login_required
def editar_colaborador(request, id):
    if not request.user.is_staff:
        messages.error(request, "Apenas administradores podem editar colaboradores.")
        return redirect('lista_colaboradores')

    colaborador = get_object_or_404(Colaborador, id=id)

    if request.method == 'POST':
        form = ColaboradorForm(request.POST, instance=colaborador)
        if form.is_valid():
            form.save()
            messages.success(request, f"Dados de {colaborador.nome_completo} atualizados com sucesso!")
            return redirect('lista_colaboradores')
    else:
        form = ColaboradorForm(instance=colaborador)

    return render(request, 'form_colaborador.html', {
        'form': form,
        'titulo': f'Editar Colaborador: {colaborador.nome_completo}'
    })


@login_required
def excluir_colaborador(request, id):
    if not request.user.is_staff:
        messages.error(request, "Apenas administradores podem excluir colaboradores.")
        return redirect('lista_colaboradores')

    colaborador = get_object_or_404(Colaborador, id=id)
    nome = colaborador.nome_completo
    if colaborador.usuario:
        colaborador.usuario.delete()
    else:
        colaborador.delete()

    messages.info(request, f"Colaborador {nome} foi removido.")
    return redirect('lista_colaboradores')


@login_required
def lista_horas(request):
    status_filtro = request.GET.get('status', 'TODOS').upper()
    valid_statuses = ['PEN', 'APR', 'AJU']

    if request.user.is_staff:
        tipo_visao = "Visão Geral de Administrador (Total por Funcionário)"
        colaboradores_horas = []
        total_geral = 0
        total_pendencias = 0

        for colab in Colaborador.objects.all().order_by('nome_completo'):
            qs = colab.registrohora_set.all()
            if status_filtro in valid_statuses:
                qs = qs.filter(status=status_filtro)
            registros = list(qs.order_by('-data'))

            if registros:
                subtotal = sum(r.horas_trabalhadas for r in registros)
                pendentes = sum(1 for r in registros if r.status == 'PEN')
                total_geral += subtotal
                total_pendencias += pendentes

                colaboradores_horas.append({
                    'colaborador': colab,
                    'registros': registros,
                    'total_horas': subtotal,
                    'total_registros': len(registros),
                    'pendentes': pendentes,
                })

        return render(request, 'lista_horas.html', {
            'colaboradores_horas': colaboradores_horas,
            'total_horas': total_geral,
            'total_pendencias': total_pendencias,
            'tipo_visao': tipo_visao,
            'status_filtro': status_filtro,
        })

    else:
        tipo_visao = "Visão do Consultor (Minhas Horas)"
        colaborador = Colaborador.objects.filter(usuario=request.user).first()
        qs = RegistroHora.objects.filter(colaborador=colaborador) if colaborador else RegistroHora.objects.none()

        if status_filtro in valid_statuses:
            qs = qs.filter(status=status_filtro)

        horas = list(qs.order_by('-data'))
        total_horas = sum(item.horas_trabalhadas for item in horas)
        total_pendencias = sum(1 for item in horas if item.status == 'PEN')

        return render(request, 'lista_horas.html', {
            'horas': horas,
            'total_horas': total_horas,
            'total_pendencias': total_pendencias,
            'tipo_visao': tipo_visao,
            'status_filtro': status_filtro,
        })


@login_required
def aprovar_hora(request, id):
    if not request.user.is_staff:
        messages.error(request, "Apenas administradores podem aprovar registros de horas.")
        return redirect('lista_horas')

    registro = get_object_or_404(RegistroHora, id=id)
    registro.status = 'APR'
    registro.save()

    messages.success(request, f"Apontamento de {registro.horas_trabalhadas}h do projeto '{registro.nome_projeto}' foi aprovado!")
    return redirect('lista_horas')


@login_required
def registrar_horas(request):
    colaborador_vinculado = None
    if not request.user.is_staff:
        colaborador_vinculado = Colaborador.objects.filter(usuario=request.user).first()

    if request.method == 'POST':
        form = RegistroHoraForm(request.POST, user=request.user)
        if form.is_valid():
            registro = form.save(commit=False)
            if not request.user.is_staff and colaborador_vinculado:
                registro.colaborador = colaborador_vinculado
                registro.status = 'PEN'
            registro.save()
            messages.success(request, f"Apontamento de {registro.horas_trabalhadas}h registrado com sucesso!")
            return redirect('lista_horas')
    else:
        dados_iniciais = {}
        if not request.user.is_staff and colaborador_vinculado:
            dados_iniciais['colaborador'] = colaborador_vinculado
            dados_iniciais['status'] = 'PEN'

        form = RegistroHoraForm(initial=dados_iniciais, user=request.user)

    return render(request, 'form_horas.html', {
        'form': form,
        'titulo': 'Registrar Atividade e Horas',
        'colaborador_fixo': colaborador_vinculado if not request.user.is_staff else None
    })


@login_required
def editar_horas(request, id):
    registro = get_object_or_404(RegistroHora, id=id)

    if not request.user.is_staff and registro.colaborador.usuario != request.user:
        messages.error(request, "Você não tem permissão para editar apontamentos de outros colaboradores.")
        return redirect('lista_horas')

    if request.method == 'POST':
        form = RegistroHoraForm(request.POST, instance=registro, user=request.user)
        if form.is_valid():
            reg_salvo = form.save(commit=False)
            if not request.user.is_staff:
                reg_salvo.status = 'PEN'
            reg_salvo.save()
            messages.success(request, f"Registro do projeto '{reg_salvo.nome_projeto}' atualizado com sucesso!")
            return redirect('lista_horas')
    else:
        form = RegistroHoraForm(instance=registro, user=request.user)

    return render(request, 'form_horas.html', {
        'form': form,
        'titulo': f'Editar Horas: {registro.nome_projeto}'
    })


@login_required
def excluir_horas(request, id):
    registro = get_object_or_404(RegistroHora, id=id)

    if not request.user.is_staff and registro.colaborador.usuario != request.user:
        messages.error(request, "Você não tem permissão para excluir apontamentos de outros colaboradores.")
        return redirect('lista_horas')

    projeto = registro.nome_projeto
    registro.delete()
    messages.info(request, f"Apontamento do projeto '{projeto}' foi excluído.")
    return redirect('lista_horas')
