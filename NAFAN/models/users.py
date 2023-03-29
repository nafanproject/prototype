from django import forms
from django.db import models
from django.forms import ModelForm

from django.views.generic.edit import CreateView, UpdateView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.db import models

from NAFAN.models import Repository, User_Repositories

from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser

from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    is_site_admin = models.BooleanField(_('site admin'), default=False)
    user_type = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=10, blank=False, default='Inactive')
    notes = models.TextField(blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def GetUsers(searchField, searchTerm, status):

        results = []
        if searchTerm:
            if searchField == "email":
                if status:
                    results = User.objects.filter(email__icontains=searchTerm).filter(status=status).order_by('email')
                else:
                    results = User.objects.filter(email__icontains=searchTerm).order_by('email')
            else:
                if status:
                    results = User.objects.filter(full_name__icontains=searchTerm).filter(status=status).order_by('email')
                else:
                    results = User.objects.filter(full_name__icontains=searchTerm).order_by('email')
        else:
            if status:
                results = User.objects.filter(status=status).order_by('email')
            else:
                results = User.objects.all().order_by('email')

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
                    user_add = User.GetUser(user.user_name)
                    results.append(user_add)

        return results

    def GetUser(username):

        user = None
        try:
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            pass;

        return user

USER_TYPES = [('contributor', 'Contributor'), ('contributor_admin', 'Contributor Admin'), ('nafan_admin', 'Nafan Admin')]
STATUS = [('Active', 'Active'), ('Inactive', 'Inactive')]

class UserForm(ModelForm):
    
    class Meta:
        model = User
        fields = '__all__'
        
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control ex_large_field'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'user_type': forms.Select(choices=USER_TYPES),
            'password': forms.PasswordInput(attrs={'class': 'form-control large_field'}),
            'status': forms.Select(choices=STATUS),
            'notes': forms.Textarea(attrs={'class': 'form-control large_field'}),
        }

class UserCreation(CreateView):
    model = User
    form_class = UserForm
    success_url = reverse_lazy('users')

class UserUpdate(UpdateView):
    model = User
    form_class = UserForm
    success_url = reverse_lazy('users')

# Bad form to delete users as it typically screws up audit history
# class UserDelete(DeleteView):
#     model = User
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
            'password': forms.PasswordInput(attrs={'class': 'form-control large_field'}),
        }

