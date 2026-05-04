from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='Email',
        help_text='Обязательное поле. Введите действующий адрес.'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'job_title', 'description', 'telegram_id')
        labels = {
            'avatar': 'Фото профиля',
            'job_title': 'Должность',
            'description': 'О себе',
            'telegram_id': 'Telegram ID',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }