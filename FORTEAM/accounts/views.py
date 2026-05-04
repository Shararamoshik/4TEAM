from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, UserEditForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.db.models import Q
from tasks.models import Task
from projects.models import Project, Permission
from .models import Profile
from django.contrib import messages


def home(request):
    context = {}
    if request.user.is_authenticated:
        user = request.user

        # 1. Активные проекты, где участвует пользователь (через модель Permission)
        active_projects = Project.objects.filter(
            permissions__user=user,
            is_active=True
        ).distinct().order_by('-created_at')[:6]

        # 2. Всего проектов с участием пользователя
        projects_count = Project.objects.filter(
            permissions__user=user
        ).distinct().count()

        # 3. Задачи, где пользователь — исполнитель
        tasks_count = Task.objects.filter(assignee=user).count()

        # 4. Последние 5 задач (исполнитель ИЛИ автор)
        last_tasks = Task.objects.filter(
            Q(assignee=user) | Q(reporter=user)
        ).distinct().order_by('-created_at')[:5]

        # 5. Профиль (может отсутствовать, используем getattr)
        profile = getattr(user, 'profile', None)

        context.update({
            'active_projects': active_projects,
            'projects_count': projects_count,
            'tasks_count': tasks_count,
            'last_tasks': last_tasks,
            'profile': profile,
        })

    return render(request, 'home.html', context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Автоматически авторизуем после регистрации
            login(request, user)
            # Перенаправление на главную или куда нужно
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def profile_view(request):
    user = request.user
    # Получаем или создаём профиль (на случай, если его ещё нет)
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлён.')
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileEditForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'profile.html', context)