from django import forms
from .models import Project, Task

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'client_name', 'status', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type':'date', 'class':'form-control'}),
            'end_date': forms.DateInput(attrs={'type':'date', 'class':'form-control'}),
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'client_name': forms.TextInput(attrs={'class':'form-control'}),
            'status': forms.Select(attrs={'class':'form-select'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'project', 'assigned_to', 'status', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'project': forms.Select(attrs={'class':'form-select'}),
            'assigned_to': forms.TextInput(attrs={'class':'form-control'}),
            'status': forms.Select(attrs={'class':'form-select'}),
            'due_date': forms.DateInput(attrs={'type':'date', 'class':'form-control'}),
        }
