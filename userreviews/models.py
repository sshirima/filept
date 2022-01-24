from django.db import models

from django.db.models.signals import pre_delete
from django.dispatch import receiver

SYSTEM_TYPE_CHOICES = (
    ("OS", "Operating Sytem"),
    ("APP", "Application"),
    ("DB", "Database")
)
AUTH_TYPE_CHOICES = (
    ("active_directory", "active_directory"),
    ("local", "local"),
    ("u2020", "Huawei EMS u2020")
)

# Create your models here.

class Account(models.Model):
    username = models.CharField(max_length=20)
    fullname = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    mobile_phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=20, blank=True, null=True)
    manager = models.CharField(max_length=20, blank=True, null=True)
    account_type = models.CharField(max_length = 20, choices = AUTH_TYPE_CHOICES,blank=True, null=True)
    date_password_expiry = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('username', 'account_type')

    def __str__(self):
        return self.username


class System(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class SystemType(models.Model):
    name = models.CharField(max_length=200, unique=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    system_type = models.CharField(max_length = 20, choices = SYSTEM_TYPE_CHOICES,blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'SystemType'
        verbose_name_plural = 'SystemTypes'


class ExportedFile(models.Model):
    name = models.CharField(max_length=100, unique=True)
    path = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
        

class SystemAccount(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    system = models.ForeignKey(System, on_delete=models.CASCADE)
    date_created = models.DateTimeField(blank=True, null=True)
    date_last_logon = models.DateTimeField(blank=True, null=True)
    date_password_expiry = models.DateTimeField(blank=True, null=True)
    password_status = models.CharField(max_length=20, blank=True, null=True)
    account_status = models.CharField(max_length=20, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.system.name+ ':' + self.account.username

    class Meta:
        verbose_name = 'SystemAccount'
        verbose_name_plural = 'SystemAccounts'
