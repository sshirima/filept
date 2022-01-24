import django_tables2 as tables
import userreviews.models as ur_models
from django.utils.safestring import mark_safe

class StatusColumn(tables.Column):
    def render(self, value):

        if value.lower() == 'active':
            return mark_safe('<span class="badge badge-success">{}</span>'.format(value))
        elif value.lower() == 'inactive':
            return mark_safe('<span class="badge badge-warning">{}</span>'.format(value))
        elif value.lower() == 'expired':
            return mark_safe('<span class="badge badge-danger">{}</span>'.format(value))
        else :
            return mark_safe('<span class="badge badge-secondary">{}</span>'.format(value))

class SystemAccountTable(tables.Table):
    username = tables.Column(accessor='account.username', verbose_name='Username')
    fullname = tables.Column(accessor='account.fullname',verbose_name='Full Name')
    system = tables.Column(accessor='system.name', verbose_name='System')
    date_last_logon = tables.Column(accessor='date_last_logon', verbose_name='Last Login')
    account_status = StatusColumn(accessor='account_status', verbose_name='Account Status')
    password_status = StatusColumn(accessor='password_status', verbose_name='Password Status')
    
    class Meta:
        model = ur_models.SystemAccount
        template_name = "django_tables2/bootstrap4.html"
        #template_name = "django_tables2/bootstrap-responsive.html"
        #template_name = "django_tables2/semantic.html"
        fields = ("username",'fullname','date_last_logon' )
        sequence = ("fullname", "username", 'system' , 'date_last_logon','account_status','password_status')
