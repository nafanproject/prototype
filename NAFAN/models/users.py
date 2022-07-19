from django import forms
from django.db import models
from django.forms import ModelForm

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import models
from pkg_resources import resource_listdir

from NAFAN.models import Repository, User_Repositories

class NAFANUser(models.Model):

    email = models.EmailField()
    full_name = models.CharField(max_length=255, blank=True)
    user_type = models.CharField(max_length=32, blank=True)
    password = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=10, blank=False, default='Inactive')
    notes = models.TextField(blank=True)

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

    def GetUsersByContributor(email, searchField, searchTerm, status):

        results = []

        # needs to be a check to make sure the same user isn't being added from two repositories
        
        repositories = Repository.GetUserRepositories(email)
        for repo in repositories:
            users = User_Repositories.GetUsers(repo.id)
            for user in users:
                # Lame way to check for duplicates
                found = False
                for existing_user in results:
                    if (existing_user.email == user.user_name):
                        found = True
                if not found:
                    user_add = NAFANUser.GetUser(user.user_name)
                    results.append(user_add)

        # if searchTerm:
        #     if searchField == "email":
        #         if status:
        #             results = NAFANUser.objects.filter(email__icontains=searchTerm).filter(status=status).order_by('email')
        #         else:
        #             results = NAFANUser.objects.filter(email__icontains=searchTerm).order_by('email')
        #     else:
        #         if status:
        #             results = NAFANUser.objects.filter(full_name__icontains=searchTerm).filter(status=status).order_by('email')
        #         else:
        #             results = NAFANUser.objects.filter(full_name__icontains=searchTerm).order_by('email')
        # else:
        #     if status:
        #         results = NAFANUser.objects.filter(status=status).order_by('email')
        #     else:
        #         results = NAFANUser.objects.all().order_by('email')

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
            'notes': forms.Textarea(attrs={'class': 'form-control large_field'}),
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

