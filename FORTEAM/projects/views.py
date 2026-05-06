from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, Permission, Invite
from tasks.models import Task
from .forms import ProjectForm, InviteForm
from django.contrib import messages
from django.http import Http404, HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

@login_required
def project_list(request):
    user = request.user

    if 'q' in request.GET:
        search_query = request.GET.get('q', '').strip()
        if search_query == '':
            request.session['reset'] = True  # пометка для удаления cookie позже
    else:
        search_query = request.COOKIES.get('project_search', '').strip()

    projects = Project.objects.filter(
        permissions__user=user,
        is_active=True
    ).distinct().order_by('-created_at')

    if search_query:
        projects = projects.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    paginator = Paginator(projects, 9)
    page_number = request.GET.get('page', 1)
    try:
        page_projects = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_projects = paginator.page(1)

    context = {
        'projects': page_projects,
        'search_query': search_query,
    }

    response = render(request, 'project_list.html', context)

    if 'q' in request.GET and search_query == '':
        response.delete_cookie('project_search')
    elif search_query:
        response.set_cookie('project_search', search_query, max_age=30*24*3600)

    return response



@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            # Создаём проект вручную
            project = Project.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data.get('description', ''),
                created_by=request.user,
                is_active=True
            )
            # Даём роль менеджера
            Permission.objects.create(
                user=request.user,
                project=project,
                role='admin'
            )
            messages.success(request, f'Проект «{project.name}» создан.')
            return redirect('project_list')
    else:
        form = ProjectForm()

    return render(request, 'project_create.html', {'form': form})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user = request.user

    # Проверка: пользователь должен быть участником проекта
    if not Permission.objects.filter(user=user, project=project).exists():
        raise Http404("Проект не найден или у вас нет доступа")

    # Получаем задачи проекта, группируем по статусам
    tasks = Task.objects.filter(project=project).select_related('assignee').order_by('-priority', 'due_date')

    todo_tasks = [t for t in tasks if t.status == Task.Status.TODO]
    in_progress_tasks = [t for t in tasks if t.status == Task.Status.IN_PROGRESS]
    done_tasks = [t for t in tasks if t.status == Task.Status.DONE]

    # Проверка: является ли пользователь админом в проекте
    is_admin = Permission.objects.filter(
        user=user, project=project, role='admin'
    ).exists()

    context = {
        'project': project,
        'todo_tasks': todo_tasks,
        'in_progress_tasks': in_progress_tasks,
        'done_tasks': done_tasks,
        'is_admin': is_admin,
    }
    return render(request, 'project_detail.html', context)


@login_required
def invite_create(request):
    user = request.user
    # Получаем проекты, где пользователь админ
    if not Project.objects.filter(permissions__user=user, permissions__role='admin').exists():
        return HttpResponseForbidden("Нужны права администратора проекта")

    if request.method == 'POST':
        form = InviteForm(request.POST, user=user)
        if form.is_valid():
            invite = form.save(commit=False)
            invite.created_by = user
            invite.save()
            invite_url = request.build_absolute_uri(
                f'/invite/{invite.token}/'
            )
            messages.success(request, f'Пригласительная ссылка создана: {invite_url}')
            return render(request, 'invite_create.html', {
                'form': form,
                'invite_url': invite_url,
            })
    else:
        form = InviteForm(user=user)

    return render(request, 'invite_create.html', {'form': form})


def invite_accept(request, token):
    invite = get_object_or_404(Invite, token=token, is_active=True)
    project = invite.project

    # Если пользователь не авторизован — перенаправляем на вход с последующим возвратом
    if not request.user.is_authenticated:
        return redirect(f'/accounts/login/?next={request.path}')

    # Проверяем, не является ли уже участником
    if Permission.objects.filter(user=request.user, project=project).exists():
        messages.info(request, f'Вы уже участник проекта «{project.name}»')
    else:
        Permission.objects.create(
            user=request.user,
            project=project,
            role='developer'   # или какую роль давать по умолчанию
        )
        messages.success(request, f'Вы присоединились к проекту «{project.name}»')

    # Деактивируем ссылку после использования (можно не деактивировать, чтобы было многоразово)
    # invite.is_active = False
    # invite.save()

    return redirect('project_detail', pk=project.pk)

@login_required
def manage_members(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not Permission.objects.filter(user=request.user, project=project, role='admin').exists():
        return HttpResponseForbidden("Только администратор может управлять участниками")
    members = Permission.objects.filter(project=project).select_related('user')
    return render(request, 'manage_members.html', {'project': project, 'members': members})

@login_required
def member_change_role(request, pk, user_id):
    project = get_object_or_404(Project, pk=pk)
    if not Permission.objects.filter(user=request.user, project=project, role='admin').exists():
        return HttpResponseForbidden()
    permission = get_object_or_404(Permission, project=project, user_id=user_id)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['admin', 'manager', 'developer', 'observer']:
            permission.role = new_role
            permission.save()
            messages.success(request, f'Роль пользователя {permission.user.username} изменена на {new_role}.')
    return redirect('manage_members', pk=project.pk)

@login_required
def member_remove(request, pk, user_id):
    project = get_object_or_404(Project, pk=pk)
    if not Permission.objects.filter(user=request.user, project=project, role='admin').exists():
        return HttpResponseForbidden()
    permission = get_object_or_404(Permission, project=project, user_id=user_id)
    if permission.user == request.user:
        messages.error(request, 'Нельзя удалить самого себя.')
    else:
        permission.delete()
        messages.success(request, f'Пользователь {permission.user.username} удалён из проекта.')
    return redirect('manage_members', pk=project.pk)