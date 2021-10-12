from django import forms
from django.db import models
from django.forms import ModelForm

class RepositoryApplication(models.Model):

    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    repository_name = models.CharField(max_length=255)
    message = models.TextField(blank=True)

    def __str__(self):
        return self.full_name

class RepositoryApplicationForm(ModelForm):
    class Meta:
        model = RepositoryApplication
        fields = '__all__'
        
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'email': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'repository_name': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'cols': '5'}),
        }
