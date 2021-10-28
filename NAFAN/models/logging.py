import datetime

from django.db import models

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