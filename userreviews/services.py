from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db import transaction
from userreviews.models import Account, System,  SystemAccount
import userreviews.datetime as dt
import userreviews.selectors as selector
import csv
from django.db import transaction
from django.conf import settings
from datetime import datetime
import pandas as pd
import numpy as np
import userreviews.logs_parser as parser


columns_ad = {
    'username':'SAM Account Name',
    'fullname':'Full Name',
    'email':'Email Address',
    'mobile_phone':'Mobile',
    'company':'Company',
    'department':'Department',
    'manager':'Manager',
    'date_created':'When Created',
    'date_last_logon':'Last Logon Time',
    'date_password_expiry':'Password Expiry Date',
    'password_status':'Password Status',
    'account_status':'Account Status',
}

columns_ur = {
    'username':'Username',
    'fullname':'Full Name',
    'email':'Email Address',
    'company':'Company',
    'department':'Department',
    'manager':'Manager',
    'date_created':'Date Created',
    'date_last_logon':'Last Logon',
    'date_password_change':'Last Password Change',
    'date_password_expiry':'Password Expiry Date',
    'password_status':'Password Status',
    'account_status':'Account Status',
    'auth_type':'Authentication Mechanism'
}

def import_ad_data_from_csv(filepath, columns_map):

    models = []
    with transaction.atomic():

        with open(filepath) as csvfile:
            csv_rows = csv.DictReader(csvfile)
            for row in csv_rows:
                try:

                    model_field ={'date_created':{'type':'date'}, 'date_last_logon':{'type':'date'}, 'date_password_expiry':{'type':'date'}, 'password_status':{}, 'account_status':{}}

                    created_account = create_account_from_csv(row, columns_map, 'active_directory' ,None)

                    if created_account is not None:
                        models.append(created_account)
                    
                except KeyError as e:
                    print("Error, KeyError: {}".format(str(e)))
                    break

    return models

def import_system_data_from_csv(filepath, columns_map, system_name=''):
   
    system = selector.get_system_by_name(system_name)

    models = []
    with transaction.atomic():

        with open(filepath) as csvfile:
            csv_rows = csv.DictReader(csvfile)
            for row in csv_rows:
                try:
                    model_field ={'date_created':{'type':'date'}, 'date_last_logon':{'type':'date'}, 'date_password_expiry':{'type':'date'}, 'password_status':{}, 'account_status':{}}

                    if  system is None:
                        print('Error, system does not exist:{}'.format(system_name))
                        break

                    if row[columns_map['auth_type']] in ['TACACS-AD', 'AD', 'VCTZ']:
                        account_type = 'active_directory'
                    else:
                        account_type = 'local'

                    created_account = create_account_from_csv(row, columns_map, account_type ,system)
                    
                    default_values = get_data_from_csv_row(row, columns_map, model_field)

                    system_account = create_update_system_account(created_account, system, default_values)

                    if system_account is not None:
                        models.append(system_account)
                    
                except KeyError as e:
                    print("Error, KeyError: {}".format(str(e)))
                    break

    return models


def create_account_from_csv(row, columns_map, account_type, system):

    model_field ={'fullname':{}, 'email':{}, 'mobile_phone':{}, 'company':{}, 'department':{},'manager':{}, 'date_password_expiry':{'type':'date'}}

    default_values = get_data_from_csv_row(row, columns_map, model_field)
    
    if system is not None:
        username = get_formated_username(account_type, row[columns_map['username']], system.name)
    else:
        username = get_formated_username(account_type, row[columns_map['username']])

    created_account = create_update_account_db(username =username, account_type=account_type, defaults=default_values)
    
    return created_account

def get_data_from_csv_row(row_data, row_columns, fields):
    values = {}
    for key, val in fields.items():
        try:
            if 'type' in val and val['type'] == 'date' and row_columns[key] in row_data:
                values[key] = dt.get_datetime_no_format(row_data[row_columns[key]])
                continue
            values[key] = row_data[row_columns[key]]
        except KeyError:
            continue
    return values


def create_system(system_name, description=''):
    if system_name == '':
        print('Error creating system, sytem name can not be empty')
        return None

    sys, created = System.objects.update_or_create(name=system_name, defaults={'description':description})
    return sys
    


def create_update_account_db(username, account_type,  defaults):

    if username == '':
        print('Error, empty string')
        return None

    try:
        created_account, created = Account.objects.update_or_create(username=username,account_type=account_type, defaults=defaults)
        print("Success, account created/Updated:{}".format(username))
        return created_account
    
    except Exception as e:
        print('Error, {}'.format(str(e)))
        return None

def get_formated_username(account_type, username, system_name=''):

    if '\\' in username:
        return username

    if account_type == 'active_directory':
        return '{}\\{}'.format('VCTZ', username)
    else:
        return '{}\\{}'.format(system_name, username)

def create_update_system_account(account, system, default_values):

    if account is None:
        print('Error, account can not be None')
        return None

    if system is None:
        print('Error, system can not be None')
        return None

    if isinstance(system, str):
        system_name = system
        system = selector.get_system_by_name(system_name)

    if isinstance(account, str):

        username = get_formated_username(default_values['account_type'], account, system.name)

        account = selector.get_account_by_username(username =account, account_type=default_values['account_type'])
        
        if account is None:
            #create new account
            account = create_update_account_db(username =username, account_type=default_values['account_type'], defaults={})
        
    if isinstance(default_values['date_last_logon'], str):
        default_values['date_last_logon'] = dt.get_datetime_no_format(default_values['date_last_logon'])

    try:
        fields = {'date_created':{}, 'date_last_logon':{},'date_password_expiry':{},'password_status':{},'account_status':{},'date_updated':{}}
        values = {}
        for key, val in fields.items():
            if key in default_values:
                values[key] = default_values[key]

        created_account, created = SystemAccount.objects.update_or_create(account=account ,system = system, defaults=values)
        if created:
            print('Success, SystemAccount created:{}>{}'.format(system.name, account.username))
        else:
            print('Success, SystemAccount updated:{}>{}'.format(system.name, account.username))
        return created_account
    
    except Exception as e:
        print('Error, {}'.format(str(e)))
        return None


columns = {
    'username': 'username',
    'account_status': 'account_status',
    'last_logon': 'last_logon',
    'account_type': 'account_type',
    'fullname': 'fullname',
    'inactive_days':'inactive_days',
}

def review_account_status(user_accounts, operation_logs, review_date):
 
        columns_temp = {
            'last_login_x':'last_logon_x',
            'last_login_y':'last_logon_y',
            'type_x':'account_type_x',
            'type_y':'account_type_y',
            
        }
        
        user_accounts[columns['last_logon']] = pd.to_datetime(user_accounts[columns['last_logon']]).dt.date
        #review_date = datetime.now()#dt.get_datetime_no_format('2021-')

        account_active_age = settings.USER_REVIEW_POLICY_SETTINGS['UNUSED_ACCOUNT_LOCKOUT_PERIOD']

        ur = pd.merge(user_accounts, operation_logs, on='username', how='outer')

        ur[columns_temp['last_login_x']] = pd.to_datetime(ur[columns_temp['last_login_x']])

        ur[columns_temp['last_login_y']] = pd.to_datetime(ur[columns_temp['last_login_y']])

        ur[columns_temp["last_login_y"]] = ur[columns_temp["last_login_y"]].fillna(pd.to_datetime('2000-01-01'))
        ur[columns_temp["last_login_x"]] = ur[columns_temp["last_login_x"]].fillna(pd.to_datetime('2000-01-01'))

        #Replace last logon date
        ur[columns['last_logon']] = np.where(ur[columns_temp['last_login_y']]>ur[columns_temp['last_login_x']], ur[columns_temp['last_login_y']], ur[columns_temp['last_login_x']])
        #Replace account type
        ur[columns['account_type']] = np.where(ur[columns_temp['type_y']].isnull(), ur[columns_temp['type_x']], ur[columns_temp['type_y']])
        ur[columns['account_type']] = np.where(ur[columns_temp['type_x']].isnull(), ur[columns_temp['type_y']], ur[columns_temp['type_x']])

        ur[columns['inactive_days']] = (review_date - ur[columns['last_logon']]).dt.days
        ur.loc[((review_date - ur[columns['last_logon']]).dt.days <= account_active_age), columns['account_status']] = 'Active'

        ur.loc[((review_date - ur[columns['last_logon']]).dt.days > account_active_age), columns['account_status']] = 'Inactive'

        ur[columns['last_logon']] = pd.to_datetime(ur[columns['last_logon']]).dt.date

        ur = ur.drop(columns = [columns_temp['type_x'],columns_temp['type_y'],columns_temp['last_login_x'], columns_temp['last_login_y']])

        return ur


def update_user_review_data_db(user_review, system_name):
    print('Reviewing accounts')
    accounts = []
    with transaction.atomic():
    
        for index, row in user_review.iterrows():
            default_values = {'date_last_logon':str(row['last_logon']), 'account_type':row['account_type'], 'account_status':row['account_status']}
            system_account = create_update_system_account( row['username'], system_name, default_values)
            accounts.append(system_account)

    return accounts


def parse_system_logs(system_name, log_file_path):

    if system_name == 'solarwinds':
        return parser.parse_solarwinds_logs(log_file_path)

    if system_name == 'ise':
        return parser.parse_cisco_ise_logs(log_file_path)

    if system_name in ['MbeziUS9810', 'KwaleUSN9810','	Mbezi_UGW','Kwale_UGW']:
        return parser.parse_epc_logs(log_file_path, system_name)
    
    if system_name in ['WIN-Q5K8NDDGDGH']:
        return parser.parse_windows_logs(log_file_path, system_name)

    return None

def update_system_accounts(system_name, operation_logs, review_date):

    review_date = dt.convert_datetime_to_date(date_time=review_date)

    system_accounts = selector.get_system_accounts_as_pandas(system_name)

    review_accounts = review_account_status(system_accounts, operation_logs, review_date)

    return update_user_review_data_db(review_accounts, system_name)