from django.contrib import admin
from userreviews.models import Account, System, ExportedFile, SystemType
import userreviews.models as u_models

from django.utils.html import format_html
from django.urls import reverse
import os

# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('username','fullname', 'email', 'mobile_phone','department','account_type')
    search_fields = ('username',)

#@admin.register(u_models.ADAccount)
#class ADAccountAdmin(admin.ModelAdmin):
#    list_display = ('account','fullname')
#    search_fields = ('account__username',)
#
#    @admin.display(ordering='account__fullname', description='Fullname')
#    def fullname(self, obj):
#        return obj.account.fullname


@admin.register(u_models.SystemAccount)
class SystemAccountAdmin(admin.ModelAdmin):
    list_display = ('account','system_name','fullname','date_last_logon','date_updated',)
    search_fields = ('account__username','system__name')

    @admin.display(ordering='account__username', description='Username')
    def username (self, obj):
        return obj.account.username

    @admin.display(ordering='account__fullname', description='Fullname')
    def fullname(self, obj):
        return obj.account.fullname

    @admin.display(ordering='system__name', description='System Name')
    def system_name(self, obj):
        return obj.system.name

#@admin.register(u_models.SystemADaccount)
#class SystemADaccountAdmin(admin.ModelAdmin):
#    list_display = ('username', 'system_name', 'fullname','date_last_logon','date_updated')
#    search_fields = ('adaccount__account__fullname','system__name')
#
#    @admin.display(description='Username')
#    def username(self, obj):
#        return obj.adaccount.account.username
#
#    @admin.display(description='Fullname')
#    def fullname(self, obj):
#        return obj.adaccount.account.fullname
#
#    @admin.display(description='System Name')
#    def system_name(self, obj):
#        return obj.system.name


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ('name',  'description')
    search_fields = ('name',  'description')

#@admin.register(SystemAccount)
#class SystemAccountAdmin(admin.ModelAdmin):
#    list_display = ('account', 'system', )
#    search_fields = ('account', 'system')

@admin.register(SystemType)
class SystemTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'description', 'system_type')
    search_fields = ('name', 'title','description')



def _delete_export_file(filepath):
    if os.path.isfile(filepath):
        os.remove(filepath)
        print('Success, deleting file:{}'.format(filepath))
    else:
        print('ERROR, deleting file:{}'.format(filepath))


@admin.register(ExportedFile)
class ExportedFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'path', 'download_url')
    search_fields = ('name', 'path')

    def download_url(self, obj):
        url = reverse('download_file', kwargs={'filename': obj.name})
        return format_html("<a href='{0}'>Download</a>", url)

    def delete_queryset(self, request, queryset):
        print('========================delete_queryset========================')
        print(queryset)

        """
        you can do anything here BEFORE deleting the object(s)
        """
        for obj in queryset:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            filepath = BASE_DIR + '/media/export/' + obj.name
            _delete_export_file(filepath)
            obj.delete()

        #queryset.delete()

        """
        you can do anything here AFTER deleting the object(s)
        """

        print('========================delete_queryset========================')

