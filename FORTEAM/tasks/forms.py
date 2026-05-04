from django import forms
from django.contrib.auth import get_user_model
from .models import Task, Comment
from projects.models import Permission, Project

User = get_user_model()

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'due_date', 'assignee']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'priority': 'Приоритет',
            'due_date': 'Срок (дд.мм.гггг)',
            'assignee': 'Исполнитель',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        if project:
            self.fields['assignee'].queryset = User.objects.filter(
                project_permissions__project=project
            ).distinct()
            self.fields['assignee'].required = False

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Напишите комментарий...'}),
        }
        labels = {'text': ''}

class TaskEditForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'due_date', 'assignee']
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'status': 'Статус',
            'priority': 'Приоритет',
            'due_date': 'Срок (дд.мм.гггг)',
            'assignee': 'Исполнитель',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)
        if project:
            self.fields['assignee'].queryset = User.objects.filter(
                project_permissions__project=project
            ).distinct()
            self.fields['assignee'].required = False