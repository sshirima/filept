import pandas as pd
import numpy as np
import pathlib
from datetime import datetime
import os
import fnmatch
from django.conf import settings

export_folder = 'exports'
import_folder = 'files'

columns_logs = {
    'start_time':'Start Time',
    'username':'Username',
    'command':'Command',
    'ne_name':'NE Name',
    'result':'Result',
    'acc_type': 'Account Type',
    'department':'Department',
    'organization':'Organization',
    'prev_roles_assigned':'Previous Roles Assigned',
    'curr_roles_assigned':'Current Roles Assigned',
    'auth_mechanism':'Authentication Mechanism',
    'creation_date':'Creation date',
    'last_login':'Last Logon',
    'acc_status':'Account Status',
    'last_pwd_change':'Last Password Change',
    'pass_status':'Password Status',
    'email':'E-mail address',
}

nodes = {
    'kwale_ugw': 'Kwale_UGW',
    'mbezi_ugw':'Mbezi_UGW',
    'kwale_usn':'KwaleUSN9810',
    'mbezi_usn':'MbeziUS9810'
}

ur_policy ={
    'account_active_age':30,
    'pass_active_age':90
}


def update_account_status(node_name, operation_logs, review_date):

    previous_user_review = get_previous_user_review(node_name, get_latest_user_review_filename(export_folder,node_name))

    login_requests = get_login_requests(operation_logs, node_name)

    user_review = get_account_status(login_requests, previous_user_review, review_date)

    password_change_requests = get_password_change_requests(operation_logs)

    user_review = get_password_status(password_change_requests, user_review, review_date)

    return user_review

def run():
    filename = get_userinput_filename(
        import_folder, 'Enter the operation logs file name: ', 'Error: File does not exist or is not csv file type')

    #operation_logs = get_operation_logs(filename)

    #review_date = get_userinput_review_date('Enter review date YYYY-MM-DD: ', 'Error: Incorrect date format')

    user_review_kwale_ugw = update_account_status(nodes['kwale_ugw'], operation_logs, review_date)
    user_review_mbezi_ugw = update_account_status(nodes['mbezi_ugw'], operation_logs, review_date)
    user_review_kwale_usn = update_account_status(nodes['kwale_usn'], operation_logs, review_date)
    user_review_mbezi_usn = update_account_status(nodes['mbezi_usn'], operation_logs, review_date)

    export_file(user_review_kwale_ugw, nodes['kwale_ugw'])
    export_file(user_review_mbezi_ugw, nodes['mbezi_ugw'])
    export_file(user_review_kwale_usn, nodes['kwale_usn'])
    export_file(user_review_mbezi_usn, nodes['mbezi_usn'])

    print('Created by sshirima')

log_file_headers = {
    'start_time':'Start Time',
}

user_review_headers ={
    'username':'Username',
}

class EPCUserReview:

    def __init__(self, review_date = None, nodeName = None):
        if review_date is not None:
            self.reviewDate = datetime.strptime(review_date, '%Y-%m-%d')
        self.nodeName = nodeName

    def getOperationLogs(self, filename):
        operation_logs = pd.read_csv(filename.strip(), skip_blank_lines=True, header=5)
        operation_logs[log_file_headers['start_time']] = pd.to_datetime(operation_logs[log_file_headers['start_time']]).dt.date
        return operation_logs

    def getLastUserreview(self, filename):
        print('Reading previous user review file: {}'.format(filename))
        p_user_review = pd.read_csv(filename, skip_blank_lines=True)
        p_user_review.set_index([user_review_headers['username']])
        return p_user_review


    def reviewAccountStatus(self,  lastUserReview, operationLogs):
        login_requests = self._getLoginRequest(operationLogs)
        user_review = self._getAccountStatus(login_requests, lastUserReview)
        return user_review

    def reviewPasswordStatus(self, userReview, operationLogs):
        password_change_requests = self._getPasswordChangeRequests(operationLogs)
        user_review = self._getPasswordStatus(password_change_requests, userReview)
        return user_review

    def _getLoginRequest(self, operation_logs):

        if self.nodeName == nodes['kwale_usn'] or self.nodeName == nodes['mbezi_usn']:
            operation_logs['User'] = operation_logs['User'].str.replace('EMS\\', '', regex=False)

            logins_request = operation_logs[(operation_logs[columns_logs['ne_name']].str.contains(self.nodeName)) & (operation_logs[columns_logs['result']] == 'Succeeded')]

        else:
            logins_request = operation_logs[(operation_logs[columns_logs['ne_name']].str.contains(self.nodeName)) & (
                operation_logs[columns_logs['command']].str.contains('LGI REQUEST')) & (operation_logs[columns_logs['result']] == 'Succeeded')]

        logins_request_sorted = logins_request[['User', columns_logs['start_time']]].sort_values(
            by=['User', columns_logs['start_time']]).groupby('User', as_index=False).last()

        logins_request_sorted = logins_request_sorted.rename(
            columns={'User': columns_logs['username'], columns_logs['start_time']: columns_logs['last_login']})

        logins_request_sorted.set_index([columns_logs['username']])

        return logins_request_sorted

    def _getAccountStatus(self, login_requests, previous_user_review):

        columns_temp = {
            'last_login_x':'Last Logon_x',
            'last_login_y':'Last Logon_y',
        }

        account_active_age = settings.USER_REVIEW_POLICY_SETTINGS['UNUSED_ACCOUNT_LOCKOUT_PERIOD']

        ur = pd.merge(previous_user_review, login_requests, on=columns_logs['username'], how='outer')

        ur[columns_temp['last_login_x']] = pd.to_datetime(ur[columns_temp['last_login_x']])

        ur[columns_temp['last_login_y']] = pd.to_datetime(ur[columns_temp['last_login_y']])
        
        ur[columns_temp["last_login_y"]] = ur[columns_temp["last_login_y"]].fillna(pd.to_datetime('2000-01-01'))
        
        ur[columns_temp["last_login_x"]] = ur[columns_temp["last_login_x"]].fillna(pd.to_datetime('2000-01-01'))

        ur[columns_logs['last_login']] = np.where(ur[columns_temp['last_login_y']]>ur[columns_temp['last_login_x']], ur[columns_temp['last_login_y']], ur[columns_temp['last_login_x']])

        ur.loc[((self.reviewDate - ur[columns_logs['last_login']]).dt.days <= account_active_age), columns_logs['acc_status']] = 'Active'

        ur.loc[((self.reviewDate - ur[columns_logs['last_login']]).dt.days > account_active_age), columns_logs['acc_status']] = 'Inactive'
        
        ur[columns_logs['last_login']] = pd.to_datetime(ur[columns_logs['last_login']]).dt.date

        ur = ur.drop(columns = [columns_temp['last_login_x'], columns_temp['last_login_y']])

        ur = ur[[columns_logs['username'],columns_logs['acc_type'],columns_logs['department'],columns_logs['organization'],columns_logs['prev_roles_assigned'],columns_logs['curr_roles_assigned'],
                    columns_logs['auth_mechanism'],columns_logs['creation_date'],columns_logs['last_login'],columns_logs['acc_status'],columns_logs['last_pwd_change'],columns_logs['pass_status'],columns_logs['email']]]

        return ur

    def _getPasswordChangeRequests(self, operation_logs):

        password_change = operation_logs[(operation_logs[columns_logs['command']].str.contains('MOD PWD')) & (operation_logs[columns_logs['result']] == 'Succeeded')]

        password_change_sorted = password_change[['User', columns_logs['start_time']]].sort_values(by=['User', columns_logs['start_time']]).groupby('User', as_index=False).last()

        password_change_sorted = password_change_sorted.rename(columns={'User': columns_logs['username'], columns_logs['start_time']: columns_logs['last_pwd_change']})

        password_change_sorted.set_index([columns_logs['username']])

        return password_change_sorted


    def _getPasswordStatus(self, password_change_requests, previous_user_review):

        columns_temp = {
            'pass_change_x':'Last Password Change_x',
            'pass_change_y':'Last Password Change_y',
        }

        password_active_age = settings.USER_REVIEW_POLICY_SETTINGS['PASSWORD_AGE']
        
        updated_date = lambda pre, now: now if prev < now else prev 

        ur = pd.merge(previous_user_review, password_change_requests, on=columns_logs['username'], how='outer')

        ur[columns_temp['pass_change_x']] = pd.to_datetime(ur[columns_temp['pass_change_x']])

        ur[columns_temp['pass_change_y']] = pd.to_datetime(ur[columns_temp['pass_change_y']])

        ur[columns_logs['last_pwd_change']] = np.where(ur[columns_temp['pass_change_y']]>ur[columns_temp['pass_change_x']], ur[columns_temp['pass_change_y']], ur[columns_temp['pass_change_x']])

        ur.loc[((self.reviewDate - ur[columns_logs['last_pwd_change']]).dt.days <= password_active_age), columns_logs['pass_status']] = 'Active'

        ur.loc[((self.reviewDate - ur[columns_logs['last_pwd_change']]).dt.days > password_active_age), columns_logs['pass_status']] = 'Inactive'

        ur[columns_logs['last_pwd_change']] = pd.to_datetime(ur[columns_logs['last_pwd_change']]).dt.date
        
        ur = ur.drop(columns = [columns_temp['pass_change_x'], columns_temp['pass_change_y']])

        ur = ur[[columns_logs['username'],columns_logs['acc_type'],columns_logs['department'],columns_logs['organization'],columns_logs['prev_roles_assigned'],columns_logs['curr_roles_assigned'],
                    columns_logs['auth_mechanism'],columns_logs['creation_date'],columns_logs['last_login'],columns_logs['acc_status'],columns_logs['last_pwd_change'],columns_logs['pass_status'],columns_logs['email']]]

        return ur
