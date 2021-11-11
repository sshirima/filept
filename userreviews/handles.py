from userreviews.processors.solarwinds import SolarwindsUserReview as solarwinds
from userreviews.processors.cisco_ise import CiscoISEUserReview as ciscoISE
from userreviews.processors.usn_ugw import EPCUserReview
from userreviews.processors.windows import WindowsUserReview
from datetime import datetime
from userreviews.files import save_data_to_csv

def create_solarwinds_userreview(date, files):
    saved_files = []
    solarwindsUserReview = solarwinds(review_date=date)
    operationLogs = solarwindsUserReview.getOperationLogs(files['operation_logs_file'])
    lastUserReview = solarwindsUserReview.getLastUserreview(files['last_user_review_file'])
    userReview = solarwindsUserReview.reviewAccountStatus(lastUserReview, operationLogs)
    userReview = solarwindsUserReview.reviewPasswordStatus(userReview, files['active_directory_file'])
    saved_files.append(save_data_to_csv(userReview, 'solarwinds'))
    return saved_files

def create_ise_userreview(date, files):
    saved_files = []
    ciscIseUserReview = ciscoISE(review_date=date)
    operationLogs = ciscIseUserReview.getOperationLogs(files['operation_logs_file'])
    lastUserReview = ciscIseUserReview.getLastUserreview(files['last_user_review_file'])
    userReview = ciscIseUserReview.reviewAccountStatus(lastUserReview, operationLogs)
    userReview = ciscIseUserReview.reviewPasswordStatus(userReview, files['active_directory_file'])
    saved_files.append(save_data_to_csv(userReview, 'cisco_ise'))
    return saved_files

def create_ugw_usn_userreview(date, files):
    saved_files = []
    nodes = {
        'kwale_ugw': 'Kwale_UGW',
        'mbezi_ugw':'Mbezi_UGW',
        'kwale_usn':'KwaleUSN9810',
        'mbezi_usn':'MbeziUS9810'
    }
    for key in nodes :
        nodename = nodes[key]
        ugwUsnUserReview = EPCUserReview(review_date=date, nodeName=nodename)
        operationLogs = ugwUsnUserReview.getOperationLogs(files['operation_logs_file'])
        lastUserReview = ugwUsnUserReview.getLastUserreview(get_filename(nodename))
        userReview = ugwUsnUserReview.reviewAccountStatus(lastUserReview, operationLogs)
        userReview = ugwUsnUserReview.reviewPasswordStatus(userReview, operationLogs)
        saved_files.append(save_data_to_csv(userReview, nodename))

    return saved_files

def create_windows_userreview(date, files):
    saved_files = []
    windowsUserReview = WindowsUserReview(review_date=date)
    operationLogs = windowsUserReview.getOperationLogs(files['operation_logs_file'])
    lastUserReview = windowsUserReview.getLastUserreview(files['last_user_review_file'])
    userReview = windowsUserReview.reviewAccountStatus(lastUserReview, operationLogs)
    userReview = windowsUserReview.reviewPasswordStatus(userReview, files['active_directory_file'])
    saved_files.append(save_data_to_csv(userReview, 'windows'))
    return saved_files

cols = {
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

from django.db import transaction
from userreviews.models import Account
import csv
from datetime import datetime
from django.utils.timezone import make_aware

def update_or_create_accounts_from_csv(filepath, auth_type):
    account_models = []
    with transaction.atomic():
        with open(filepath) as csvfile:
            accounts = csv.DictReader(csvfile)
            for account in accounts:
                try:
                    account_values = {  'fullname': account[cols['fullname']],
                                        'email': account[cols['email']],
                                        'mobile_phone': account[cols['mobile_phone']],
                                        'company': account[cols['company']],
                                        'department': account[cols['department']],
                                        'manager': account[cols['manager']],
                                        'auth_type': auth_type,
                                        'date_created':get_datetime_from_string(account[cols['date_created']], "%Y-%m-%d %H:%M:%S"),
                                        'date_last_logon':get_datetime_from_string(account[cols['date_last_logon']], "%Y-%m-%d %H:%M:%S"),
                                        'date_password_expiry':get_datetime_from_string(account[cols['date_password_expiry']], "%Y-%m-%d %H:%M:%S"),
                                        'password_status': account[cols['password_status']],
                                        'account_status': account[cols['account_status']],
                                                                                 }
                except KeyError as e:
                    print("Error, KeyError: {}".format(str(e)))
                    break

                try:
                    account_name = account[cols['username']]
                    obj, created = Account.objects.update_or_create(username=account_name, defaults=account_values)
                    if created:
                        print("Success, account created:{}".format(account_name))
                    else:
                        print("Success, account updated:{}".format(account_name))
                    account_models.append(obj)
                except Exception as e:
                    print("Error, creating or updating account {}:{}".format(account_name, str(e)))
                    pass

    return account_models

def get_datetime_from_string(date_string, format):
    try:
        return make_aware(datetime.strptime(date_string, format))
    except ValueError:
        return None
    

def get_filename(name ):
    return 'media/imports/{}.csv'.format(name.upper())