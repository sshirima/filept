from django.db.models import Value, Q, F
from django import forms
import django_filters
import userreviews.models as ur_models

class SystemAccountsFilter(django_filters.FilterSet):

    username = django_filters.CharFilter(label='Username, Full name', method='search_username')
    account_status = django_filters.CharFilter(label='Account status', method='search_account_status')
    #inactive = django_filters.BooleanFilter(widget=forms.CheckboxInput, label='Inactive', method='include_inactive')
    
    def search_username(self, queryset, name, value):
        return queryset.filter(Q(account__username__icontains=value)|Q(account__fullname__icontains=value))

    def search_account_status(self, queryset, name, value):
        return queryset.filter(account_status__iexact=value)

    #def include_inactive(self, queryset, name, value):
    #    expression = Q(status__in=[1,2,5]) if value else Q(status__in=[1,5])
    #    return queryset.filter(expression)
    
    class Meta:
        model = ur_models.SystemAccount
        fields = ['username', 'account_status']