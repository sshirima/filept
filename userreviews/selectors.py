import userreviews.models as model
from django.core.exceptions import ObjectDoesNotExist
from django_pandas.io import read_frame
from django.db.models import F
import pandas as pd


def get_system_by_name(name):

    try:
        return model.System.objects.get(name=name)

    except ObjectDoesNotExist as e:
        print('Error, {}'.format(str(e)))
        return None

    except model.System.MultipleObjectsReturned:
        print('Error, {}'.format(str(e)))
        return None


def get_account_by_username(username, account_type='active_directory'):
    try:
        return model.Account.objects.get(username=username, account_type=account_type)

    except ObjectDoesNotExist as e:
        print('Error, {}'.format(str(e)))
        return None

    except model.Account.MultipleObjectsReturned:
        print('Error, {}'.format(str(e)))
        return None


def get_system_by_name(system_name):
    try:
        return model.System.objects.get(name=system_name)

    except ObjectDoesNotExist as e:
        print('Error, {}'.format(str(e)))
        return None

    except model.Account.MultipleObjectsReturned:
        print('Error, {}'.format(str(e)))
        return None



def get_system_accounts(system_name, as_pandas=False):
    try:
        system_accounts = model.SystemAccount.objects.select_related('account', 'system').filter(system__name=system_name).annotate(
            username=F('account__username'), 
            fullname=F('account__fullname'), 
            account_type=F('account__account_type'), 
            system_name=F('system__name'), 
            last_logon=F('date_last_logon'), 
            password_expiry =F('account__date_password_expiry'),
            ).values(
                'username', 
                'fullname', 
                'account_type',
                'account_status', 
                'password_status',
                'last_logon',
                'system_name',
                'password_expiry',
            )

        if as_pandas:
            system_accounts = read_frame(system_accounts)

    except ObjectDoesNotExist as e:
        print('Error, {}'.format(str(e)))
        return []

    return system_accounts

def get_system_accounts_as_pandas(system_name):

    return get_system_accounts(system_name, as_pandas=True)


#def get_system_local_accounts(system_name, as_pandas=False):
#    try:
#        local_accounts = model.Account.objects.select_related('localaccount').filter(localaccount__system__name=system_name).annotate(account_status=F('localaccount__account_status'), last_logon=F('localaccount__date_last_logon'), password_status=F('localaccount__password_status')).values(
#        'username', 'fullname', 'account_type','account_status', 'password_status','last_logon')
#
#        if as_pandas:
#            local_accounts = read_frame(local_accounts)
#
#    except ObjectDoesNotExist as e:
#        print('Error, {}'.format(str(e)))
#        return []
#
#    return local_accounts


#def get_system_ad_accounts(system_name, as_pandas=False):
#    try:
#        accounts = model.SystemADaccount.objects.select_related('adaccount', 'adaccount__account').filter(system__name=system_name).annotate(username=F(
#        'adaccount__account__username'), fullname=F('adaccount__account__fullname'),account_status=F('adaccount__account_status'), last_logon=F('date_last_logon'), password_status=F('adaccount__password_status'), account_type=F('adaccount__account__account_type')).values('username', 'fullname', 'account_type','account_status', 'password_status','last_logon')
#
#        if as_pandas:
#            accounts = read_frame(accounts)
#
#    except ObjectDoesNotExist as e:
#        print('Error, {}'.format(str(e)))
#        return []
#
#    return accounts
