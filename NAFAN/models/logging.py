import datetime

from django.db import models
from django.db.models import Q
from django import forms
from django.forms import ModelForm

class NAFANLog(models.Model):

    LOG_TYPES = (
        ('E', 'Exception'),
        ('I', 'Info'),
        ('L', 'Login'),
    )

    log_time = models.DateTimeField()
    log_type = models.CharField(max_length=1, choices=LOG_TYPES)
    log_message = models.CharField(max_length=2048)

    def LogException(exception):
        log = NAFANLog(log_time=datetime.datetime.now(), log_type='E', log_message=exception)
        log.save()

    def LogInfo(message):
        log = NAFANLog(log_time=datetime.datetime.now(), log_type='I', log_message=message)
        log.save()

    def LogLogin(user):
        log = NAFANLog(log_time=datetime.datetime.now(), log_type='L', log_message=user)
        log.save()
        
    def GetLog(searchTerm):
        if searchTerm:
            return NAFANLog.objects.filter(log_message__icontains=searchTerm).order_by('log_time')[:50]
        else:
            return NAFANLog.objects.all()[:50]

    def ClearLog(clearRange):
        if clearRange == "Saving one month":
            NAFANLog.objects.filter(log_time__lte=datetime.datetime.now() - datetime.timedelta(days=31)).delete()
        elif clearRange == "Saving one year":
            NAFANLog.objects.filter(log_time__lte=datetime.datetime.now() - datetime.timedelta(days=365)).delete()
        elif clearRange == "All":
            NAFANLog.objects.all().delete()
            
        return NAFANLog.objects.all()[:50]

class NAFANAudit(models.Model):

    USER_TARGET = "user"
    REPOSITORY_TARGET = "repository"
    FINDINGAID_TARGET = "finding aid"

    CREATE_ACTION = "create"
    UPDATE_ACTION = "update"
    ADD_REPOSITORY_ACTION = "add repository"
    REMOVE_REPOSITORY_ACTION = "remove repository"

    actor_email = models.EmailField()                   # User name of entity taking action, usually a user, but could be the system
    targetID = models.IntegerField()                    # ID of entity being acted upon
    target_type = models.CharField(max_length=10)       # Type of entity being acted upon, repository, user, etc.
    audit_action = models.CharField(max_length=10)      # What is being done create, update, inactivate, etc.
    audit_time = models.DateTimeField()
    notes = models.CharField(max_length=2048)

    def AddAudit(targetID, target_type, audit_action, actor_email, notes):
        
        audit = NAFANAudit(audit_time=datetime.datetime.now(), targetID=targetID, target_type=target_type, audit_action=audit_action, actor_email=actor_email, notes=notes)
        audit.save()

    def GetAudit(targetID, target_type):

        targetID_filter = Q(targetID=targetID)
        target_type_filter = Q(target_type=target_type)

        return NAFANAudit.objects.filter(targetID_filter & target_type_filter).order_by('-audit_time')

##############################

class NAFANContact(models.Model):

    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField(blank=True)

    def __str__(self):
        return self.full_name

class NAFANContactForm(ModelForm):
    class Meta:
        model = NAFANContact
        fields = '__all__'
        
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'email': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'subject': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'cols': '5'}),
        }

##############################

class NAFANJoinUs(models.Model):

    full_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    phone = models.CharField(max_length=25)
    url = models.CharField(max_length=255,blank=True)
    collection_guides = models.TextField()
    message = models.CharField(max_length=1024,blank=True)

    def __str__(self):
        return self.full_name

    def GetActionItems():
        return NAFANJoinUs.objects.all()


class NAFANJoinUsForm(ModelForm):
    class Meta:
        model = NAFANJoinUs
        fields = '__all__'
        
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'email': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'phone': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'url': forms.TextInput(attrs={'class': 'form-control large_field'}),
            'collection_guides': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'cols': '5'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': '3', 'cols': '5'}),
        }
