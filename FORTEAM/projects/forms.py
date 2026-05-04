from django import forms
from .models import Project
from .models import Invite

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description']
        labels = {
            'name': 'Название проекта',
            'description': 'Описание',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class InviteForm(forms.ModelForm):
    class Meta:
        model = Invite
        fields = ['project']
        labels = {
            'project': 'Проект',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Только проекты, где пользователь — администратор
            self.fields['project'].queryset = Project.objects.filter(
                permissions__user=user,
                permissions__role='admin',
                is_active=True
            ).distinct()