from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, UserEditForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.db.models import Q
from django.urls import reverse
from tasks.models import Task
from projects.models import Project, Permission
from .models import Profile, EmailVerificationToken
from django.contrib import messages
from django.core.mail import send_mail


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
            # Создаём неактивного пользователя
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Генерируем токен подтверждения
            token = EmailVerificationToken.objects.create(user=user)

            # Формируем ссылку для подтверждения
            verification_url = request.build_absolute_uri(
                reverse('verify_email', args=[token.token])
            )
            print(f"\n=== ССЫЛКА ДЛЯ ПОДТВЕРЖДЕНИЯ ===\n{verification_url}\n=============================\n")
            # Отправляем письмо (попадёт в консоль)
            send_mail(
                subject='4TEAM – Подтверждение регистрации',
                message=(
                    f'Здравствуйте, {user.username}!\n\n'
                    f'Перейдите по ссылке, чтобы активировать аккаунт:\n'
                    f'{verification_url}\n\n'
                    f'Если вы не регистрировались, просто проигнорируйте это письмо.'
                ),
                from_email='noreply@4team.local',
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.info(
                request,
                'Регистрация почти завершена! '
                'Проверьте консоль сервера (или вашу почту, если настроена отправка) '
                'и перейдите по ссылке для активации.'
            )
            return redirect('login')
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

def verify_email(request, token):
    verification = get_object_or_404(EmailVerificationToken, token=token)
    user = verification.user

    if user.is_active:
        messages.warning(request, 'Аккаунт уже активирован.')
    else:
        user.is_active = True
        user.save()
        messages.success(request, 'Email подтверждён! Теперь вы можете войти.')

    # Удаляем использованный токен
    verification.delete()
    return redirect('home')