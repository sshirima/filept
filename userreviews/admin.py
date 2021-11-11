from django.contrib import admin
from userreviews.models import Account, System, SystemAccount, ExportedFile

from django.utils.html import format_html
from django.urls import reverse
import os

# Register your models here.
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'fullname', 'email', 'auth_type', 'date_last_logon', 'date_updated')
    search_fields = ('username', 'username', 'email')


@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'description', 'system_type')
    search_fields = ('name', 'title', 'description')

@admin.register(SystemAccount)
class SystemAccountAdmin(admin.ModelAdmin):
    list_display = ('account', 'system', 'date_last_logon', 'date_password_change')
    search_fields = ('account', 'system')


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

