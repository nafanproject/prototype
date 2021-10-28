from django import forms
from django.db import models
from django.forms import ModelForm

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

class NAFANUser(models.Model):

    email = models.EmailField()
    full_name = models.CharField(max_length=255, blank=True)
    user_type = models.CharField(max_length=32, blank=True)
    password = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=10, blank=False, default='Inactive')

    def GetUsers(searchField, searchTerm, status):

        results = []
        if searchTerm:
            if searchField == "email":
                if status:
                    results = NAFANUser.objects.filter(email__icontains=searchTerm).filter(status=status).order_by('email')
                else:
                    results = NAFANUser.objects.filter(email__icontains=searchTerm).order_by('email')
            else:
                if status:
                    results = NAFANUser.objects.filter(full_name__icontains=searchTerm).filter(status=status).order_by('email')
                else:
                    results = NAFANUser.objects.filter(full_name__icontains=searchTerm).order_by('email')
        else:
            if status:
                results = NAFANUser.objects.filter(status=status).order_by('email')
            else:
                results = NAFANUser.objects.all().order_by('email')

        return results

    def GetUser(username):

        user = None
        try:
            user = NAFANUser.objects.get(email=username)
        except NAFANUser.DoesNotExist:
            pass;

        return user

USER_TYPES = [('researcher', 'Researcher'), ('contributor', 'Contributor'), ('contributor_admin', 'Contributor Admin'), ('nafan_admin', 'Nafan Admin')]
STATUS = [('Active', 'Active'), ('Inactive', 'Inactive')]

class NAFANUserForm(ModelForm):
    class Meta:
        model = NAFANUser
        fields = '__all__'
        
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'user_type': forms.Select(choices=USER_TYPES),
            'password': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'status': forms.Select(choices=STATUS),
        }

class UserCreation(CreateView):
    model = NAFANUser
    form_class = NAFANUserForm
    success_url = reverse_lazy('users')

class UserUpdate(UpdateView):
    model = NAFANUser
    form_class = NAFANUserForm
    success_url = reverse_lazy('users')

# class UserDelete(DeleteView):
#     model = NAFANUser
#     success_url = reverse_lazy('users')

class NAFANLogin(models.Model):

    email = models.EmailField()
    password = models.CharField(max_length=32, blank=True)

class NAFANLoginForm(ModelForm):
    class Meta:
        model = NAFANLogin
        fields = '__all__'
        
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'password': forms.TextInput(attrs={'class': 'form-control large_field'}),
        }

