import pandas as pd
import numpy as np
import pathlib
from datetime import datetime
import os
import fnmatch
from django.conf import settings

user_review_columns ={
    'username':'Username',
    'name':'Name/Description',
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
    'review_date':'Review date',
}


class SolarwindsUserReview:

    reviewDate = None

    def __init__(self, review_date):
        self.reviewDate = datetime.strptime(review_date, '%Y-%m-%d')

    
    def getOperationLogs(self, filename):

        file_columns = {
            'name':'NAME',
            'last_login':'LAST LOGIN',
        }

        operation_logs = pd.read_csv(filename.strip(), skip_blank_lines=True)

        operation_logs[file_columns['name']] = operation_logs[file_columns['name']].str.replace('VCTZ\\', '', regex=False)

        operation_logs = operation_logs[[file_columns['name'], file_columns['last_login']]]

        operation_logs = operation_logs.rename(
            columns={file_columns['name']: user_review_columns['username'], file_columns['last_login']: user_review_columns['last_logon']})

        operation_logs[user_review_columns['last_logon']] = pd.to_datetime(operation_logs[user_review_columns['last_logon']]).dt.date

        return operation_logs

    def getLastUserreview(self, filename):

        if not filename == '':
            print('Reading last user review file: {}'.format(filename))

            p_user_review = pd.read_csv(filename, skip_blank_lines=True)
            p_user_review[user_review_columns['account_creation']] = pd.to_datetime(p_user_review[user_review_columns['account_creation']])
            p_user_review[user_review_columns['review_date']] = pd.to_datetime(p_user_review[user_review_columns['review_date']])
            p_user_review.set_index([user_review_columns['username']])

            return p_user_review

    def reviewAccountStatus(self, lastUserreview, operationLogs):

        login_requests = self._getLoginRequests(operationLogs)

        userReview = self._getAccountStatus(login_requests, lastUserreview, self.reviewDate)

        return userReview

    def reviewPasswordStatus(self, userReview, adFile):

        password_change_requests = self._getPasswordChangeRequests(adFile)

        user_review = self._getPasswordStatus(password_change_requests, userReview, self.reviewDate)

        return user_review

    def _getLoginRequests(self, operation_logs):
    
        operation_logs = operation_logs.set_index([user_review_columns['username']])
    
        return operation_logs

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

        ur.loc[((review_date - ur[user_review_columns['last_logon']]).dt.days <= account_active_age), user_review_columns['account_status']] = 'Active'

        ur.loc[((review_date - ur[user_review_columns['last_logon']]).dt.days > account_active_age), user_review_columns['account_status']] = 'Inactive'

        ur[user_review_columns['last_logon']] = pd.to_datetime(ur[user_review_columns['last_logon']]).dt.date

        ur = ur.drop(columns = [columns_temp['last_login_x'], columns_temp['last_login_y']])

        return ur

    def _getPasswordChangeRequests(self, ad_filename):

        password_change = self._get_password_status_file(ad_filename)

        return password_change

    def _getPasswordStatus(self, password_change_requests, last_user_review, review_date):

        columns_temp = {
            'pass_status_x':'Password Status_x',
            'pass_status_y':'Password Status_y',
        }

        updated_date = lambda pre, now: now if prev < now else prev 

        ur = pd.merge(last_user_review, password_change_requests, on=user_review_columns['username'], how='left')

        ur = ur.rename(columns={columns_temp['pass_status_y']: user_review_columns['password_status']})

        ur = ur.drop(columns = [columns_temp['pass_status_x']])

        return ur

    def _get_password_status_file(self, filename):

        print('Reading AD dump file: {}'.format(filename))
    
        ad_file = pd.read_csv(
            filename.strip(), skip_blank_lines=True)
        
        ad_file = ad_file[[user_review_columns['sam_account_name'], user_review_columns['password_status']]]
    
        ad_file = ad_file.rename(columns={user_review_columns['sam_account_name']: user_review_columns['username']})
        
        return ad_file