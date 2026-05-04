from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .forms import TaskForm, CommentForm, TaskEditForm
from django.http import Http404
from .models import Task
from projects.models import Permission, Project

# Create your views here.

@login_required
def task_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    user = request.user

    # Проверка: пользователь должен быть администратором проекта
    if not Permission.objects.filter(user=user, project=project, role='admin').exists():
        return HttpResponseForbidden("Только администратор может создавать задачи")

    if request.method == 'POST':
        form = TaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.reporter = user
            task.save()
            messages.success(request, f'Задача «{task.title}» создана.')
            return redirect('project_detail', pk=project.pk)
    else:
        form = TaskForm(project=project)

    return render(request, 'task_create.html', {
        'form': form,
        'project': project,
    })

@login_required
def task_detail(request, pk):
    task = get_object_or_404(
        Task.objects.select_related('project', 'assignee', 'reporter'),
        pk=pk
    )
    project = task.project
    user = request.user

    # Проверка доступа: только участники проекта видят задачу
    if not Permission.objects.filter(user=user, project=project).exists():
        raise Http404("Задача не найдена или у вас нет доступа")

    # Администратор в этом проекте?
    is_admin = Permission.objects.filter(
        user=user, project=project, role='admin'
    ).exists()

    # Комментарии
    comments = task.comments.select_related('user').order_by('created_at')

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.task = task
            comment.user = user
            comment.save()
            messages.success(request, 'Комментарий добавлен.')
            return redirect('task_detail', pk=task.pk)
    else:
        comment_form = CommentForm()

    context = {
        'task': task,
        'is_admin': is_admin,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'task_detail.html', context)

@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task.objects.select_related('project'), pk=pk)
    project = task.project
    user = request.user

    # Проверка: пользователь должен быть администратором проекта
    if not Permission.objects.filter(user=user, project=project, role='admin').exists():
        return HttpResponseForbidden("Только администратор может редактировать задачу")

    if request.method == 'POST':
        form = TaskEditForm(request.POST, instance=task, project=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Задача «{task.title}» обновлена.')
            return redirect('task_detail', pk=task.pk)
    else:
        form = TaskEditForm(instance=task, project=project)

    return render(request, 'task_edit.html', {
        'form': form,
        'task': task,
    })

@login_required
def task_change_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    project = task.project
    user = request.user

    if not Permission.objects.filter(user=user, project=project).exists():
        return HttpResponseForbidden()

    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        if new_status in dict(Task.Status.choices):
            task.status = new_status
            task.save()
            messages.success(request, f'Статус задачи «{task.title}» изменён на {task.get_status_display()}')

    return redirect('project_detail', pk=project.pk)