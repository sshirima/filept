import pandas as pd
import numpy as np
import pathlib
from datetime import datetime
import os
import fnmatch
from django.conf import settings

user_review_columns = {
    'name':'Name/Description',
    'username':'Username',
    'nov_role_assigned':'Nov Roles Assigned',
    'roles_assigned':'Roles Assigned',
    'role_change':'Role Change',
    'account_status':'Accout status',
    'account_type':'Account Type',
    'account_creation':'Account Creation Date',
    'last_logon':'Last Logon',
    'password_status':'Password Status',
    'password_change':'Last Password Change',
    'department':'Department/Section',
    'auth_mechanism':'Authentication Mechanism',
    'email':'Email Address',
    'organisation':'Organisation',
    'sam_account_name':'SAM Account Name',
}

class CiscoISEUserReview:

    def __init__(self, review_date = None):
        if review_date is not None:
            self.reviewDate = datetime.strptime(review_date, '%Y-%m-%d')

    def getOperationLogs(self, filename):
        print('Reading ise dump file: {}'.format(filename))
        ise_logs_columns= {
            'logged_time' : 'LOGGED_TIME',
            'username':'USERNAME'
        }
        operation_logs = pd.read_csv(filename.strip(), skip_blank_lines=True)
        operation_logs = operation_logs.rename(columns=lambda x: x.replace("'","").replace('"','')).replace(" ","")
        operation_logs = operation_logs[[ise_logs_columns['logged_time'], ise_logs_columns['username']]]
        operation_logs[ise_logs_columns['logged_time']] = pd.to_datetime(operation_logs[ise_logs_columns['logged_time']]).dt.date
        return operation_logs

    def getLastUserreview(self, filename):
        print('Reading previous user riview file: {}'.format(filename))
        p_user_review = pd.read_csv(filename, skip_blank_lines=True)
        p_user_review.set_index([user_review_columns['username']])
        return p_user_review

    def reviewAccountStatus(self,  lastUserReview, operationLogs):
        login_requests = self._getLoginRequest(operationLogs)
        user_review = self._getAccountStatus(login_requests, lastUserReview)
        return user_review

    def reviewPasswordStatus(self, userReview, adFile):
        password_change_requests = self._getPasswordChangeRequests(adFile)
        user_review = self._getPasswordStatus(password_change_requests, userReview)
        return user_review

    def _getLoginRequest(self, operation_logs):

        ise_logs_columns= {
            'logged_time' : 'LOGGED_TIME',
            'username':'USERNAME'
        }

        logins_request_sorted = operation_logs[[ise_logs_columns['username'], ise_logs_columns['logged_time']]].sort_values(
            by=[ise_logs_columns['username'], ise_logs_columns['logged_time']]).groupby(ise_logs_columns['username'], as_index=False).last()

        logins_request_sorted = logins_request_sorted.rename(
            columns={ise_logs_columns['username']: user_review_columns['username'], ise_logs_columns['logged_time']: user_review_columns['last_logon']})

        logins_request_sorted[user_review_columns['username']] = logins_request_sorted[user_review_columns['username']].str.replace("'","")

        logins_request_sorted.set_index([user_review_columns['username']])

        return logins_request_sorted

    def _getAccountStatus(self, login_requests, last_user_review, review_date):

        columns_temp = {
            'last_login_x':'Last Logon_x',
            'last_login_y':'Last Logon_y',
        }

        account_active_age = settings.USER_REVIEW_POLICY_SETTINGS['UNUSED_ACCOUNT_LOCKOUT_PERIOD']

        ur = pd.merge(last_user_review, login_requests, on=user_review_columns['username'], how='outer')

        ur[columns_temp['last_login_x']] = pd.to_datetime(ur[columns_temp['last_login_x']])

        ur[columns_temp['last_login_y']] = pd.to_datetime(ur[columns_temp['last_login_y']])

        ur[columns_temp["last_login_y"]] = ur[columns_temp["last_login_y"]].fillna(pd.to_datetime('2000-01-01'))
        ur[columns_temp["last_login_x"]] = ur[columns_temp["last_login_x"]].fillna(pd.to_datetime('2000-01-01'))

        ur[user_review_columns['last_logon']] = np.where(ur[columns_temp['last_login_y']]>ur[columns_temp['last_login_x']], ur[columns_temp['last_login_y']], ur[columns_temp['last_login_x']])

        ur.loc[((self.reviewDate - ur[user_review_columns['last_logon']]).dt.days <= account_active_age), user_review_columns['account_status']] = 'Active'

        ur.loc[((self.reviewDate - ur[user_review_columns['last_logon']]).dt.days > account_active_age), user_review_columns['account_status']] = 'Inactive'

        ur[user_review_columns['last_logon']] = pd.to_datetime(ur[user_review_columns['last_logon']]).dt.date

        ur = ur.drop(columns = [columns_temp['last_login_x'], columns_temp['last_login_y']])

        return ur

    def _getPasswordStatus(self, password_change_requests, last_user_review):

        columns_temp = {
            'pass_status_x':'Password Status_x',
            'pass_status_y':'Password Status_y',
        }

        updated_date = lambda pre, now: now if prev < now else prev 

        ur = pd.merge(last_user_review, password_change_requests, on=user_review_columns['username'], how='left')
        ur = ur.rename(columns={columns_temp['pass_status_y']: user_review_columns['password_status']})
        ur = ur.drop(columns = [columns_temp['pass_status_x']])

        ur = ur[[user_review_columns['name'],
                    user_review_columns['username'],
                    user_review_columns['nov_role_assigned'],
                    user_review_columns['roles_assigned'],
                    user_review_columns['role_change'],
                    user_review_columns['account_type'],
                    user_review_columns['account_creation'],
                    user_review_columns['last_logon'],
                    user_review_columns['account_status'],
                    #user_review_columns['password_change'],
                    user_review_columns['password_status'],
                    user_review_columns['department'],
                    user_review_columns['auth_mechanism'],
                    user_review_columns['email'],
                    user_review_columns['organisation']
                    ]]

        return ur

    def _getPasswordChangeRequests(self, ad_filename):
        password_change = self._getPasswordStatusFile(ad_filename)
        return password_change

    def _getPasswordStatusFile(self, filename):
        print('Reading AD dump file: {}'.format(filename))
        ad_file = pd.read_csv(filename.strip(), skip_blank_lines=True)
        ad_file = ad_file[[user_review_columns['sam_account_name'], user_review_columns['password_status']]]
        ad_file = ad_file.rename(columns={user_review_columns['sam_account_name']: user_review_columns['username']})
        return ad_file
