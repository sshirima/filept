import pandas as pd
import numpy as np
import pathlib
from datetime import datetime
import os
import fnmatch
import xml.etree.ElementTree as Xet
import glob
from django.conf import settings

export_folder = "exports"
import_folder = "files"

user_review_columns = {
    "name": "Name/Description",
    "username": "Username",
    "domain": "Domain",
    "nov_role_assigned": "Nov Roles Assigned",
    "roles_assigned": "Roles Assigned",
    "role_change": "Role Change",
    "account_status": "Accout status",
    "account_type": "Account Type",
    "account_creation": "Account Creation Date",
    "last_logon": "Last Logon",
    "password_status": "Password Status",
    "password_change": "Last Password Change",
    "department": "Department/Section",
    "auth_mechanism": "Authentication Mechanism",
    "email": "Email Address",
    "organisation": "Organisation",
    "sam_account_name": "SAM Account Name",
    "password_last_set": "Password Last Set",
}

ur_policy = {"account_active_age": 30, "pass_active_age": 90}


def get_accounts_last_login_date(operation_logs):

    remote_desktop_logs = operation_logs[(operation_logs['LogonType'] == '10')][['TargetUserName', 'SystemTime', 'TargetDomainName']]

    remote_desktop_logs = (
        remote_desktop_logs.sort_values(by=['TargetUserName', 'SystemTime'])
        .groupby('TargetUserName', as_index=False)
        .last()
    )
    

    remote_desktop_logs = remote_desktop_logs.rename(
        columns={
            'TargetUserName': user_review_columns['username'],
            'SystemTime': user_review_columns['last_logon'],
            'TargetDomainName': 'Domain',    
        }
    )

    remote_desktop_logs.set_index(user_review_columns['username'])

    return remote_desktop_logs


def read_active_directory_file(filename):

    print("Reading AD dump file: {}".format(filename))

    ad_file = pd.read_csv(filename.strip(), skip_blank_lines=True)

    ad_file = ad_file[
        [
            user_review_columns["sam_account_name"],
            user_review_columns["password_status"],
            #user_review_columns["password_last_set"]
        ]
    ]

    ad_file = ad_file.rename(
        columns={
            user_review_columns["sam_account_name"]: user_review_columns["username"],
            #user_review_columns["password_last_set"]: user_review_columns["password_change"],
        }
    )

    #ad_file[user_review_columns["password_change"]] = pd.to_datetime(ad_file[user_review_columns["password_change"]])

    return ad_file


def get_password_change_status(ad_filename):

    password_change = read_active_directory_file(ad_filename)

    return password_change


def update_account_status(login_requests, last_user_review, review_date):

    columns_temp = {
        "last_login_x": "Last Logon_x",
        "last_login_y": "Last Logon_y",
    }

    ur = pd.merge(
        last_user_review,
        login_requests,
        on=user_review_columns["username"],
        how="outer",
    )

    ur[columns_temp["last_login_x"]] = pd.to_datetime(ur[columns_temp["last_login_x"]])
    ur[columns_temp["last_login_y"]] = pd.to_datetime(ur[columns_temp["last_login_y"]])

    ur[columns_temp["last_login_y"]] = ur[columns_temp["last_login_y"]].fillna(pd.to_datetime('2000-01-01'))
    ur[columns_temp["last_login_x"]] = ur[columns_temp["last_login_x"]].fillna(pd.to_datetime('2000-01-01'))

    ur[user_review_columns["last_logon"]] = np.where(
        ur[columns_temp["last_login_y"]] > ur[columns_temp["last_login_x"]],
        ur[columns_temp["last_login_y"]],
        ur[columns_temp["last_login_x"]],
    )

    account_active_age = settings.USER_REVIEW_POLICY_SETTINGS['UNUSED_ACCOUNT_LOCKOUT_PERIOD']
    ur.loc[
        (
            (review_date - ur[user_review_columns["last_logon"]]).dt.days
            <= account_active_age
        ),
        user_review_columns["account_status"],
    ] = "Active"

    ur.loc[
        (
            (review_date - ur[user_review_columns["last_logon"]]).dt.days
            > account_active_age
        ),
        user_review_columns["account_status"],
    ] = "Inactive"

    ur[user_review_columns["last_logon"]] = pd.to_datetime(
        ur[user_review_columns["last_logon"]]
    ).dt.date

    ur = ur.drop(columns=[columns_temp["last_login_x"], columns_temp["last_login_y"]])

    return ur


def update_password_status(password_change_requests, last_user_review, review_date):

    columns_temp = {
        "pass_status_x": "Password Status_x",
        "pass_status_y": "Password Status_y",
    }

    ur = pd.merge(
        last_user_review,
        password_change_requests,
        on=user_review_columns["username"],
        how="left",
    )
    ur = ur.rename(
        columns={columns_temp["pass_status_y"]: user_review_columns["password_status"]}
    )
    ur = ur.drop(columns=[columns_temp["pass_status_x"]])

    ur = ur[
        [
            user_review_columns["name"],
            user_review_columns["username"],
            user_review_columns["domain"],
            user_review_columns["nov_role_assigned"],
            user_review_columns["roles_assigned"],
            user_review_columns["role_change"],
            user_review_columns["account_type"],
            user_review_columns["account_creation"],
            user_review_columns["last_logon"],
            user_review_columns["account_status"],
            #user_review_columns["password_change"],
            user_review_columns["password_status"],
            user_review_columns["department"],
            user_review_columns["auth_mechanism"],
            user_review_columns["email"],
            user_review_columns["organisation"],
        ]
    ]

    return ur

def parse_xml_file(filename):

    print('Parsing file: {}'.format(filename))

    xmlparse = Xet.parse(filename)

    root = xmlparse.getroot()

    rows = []

    for event in root:

        system = event[0]

        eventdata = event[1]

        time = system[7].attrib["SystemTime"]

        computer = system[12].text

        row = {"SystemTime": time, "Computer": computer}

        for data in eventdata:

            row[data.attrib["Name"]] = data.text

        rows.append(row)

        row = {}
    return rows

def get_daily_logs(logs_files):

    logs = []

    for log_file in logs_files:

        d_logs = parse_xml_file(log_file)

        logs.append(d_logs)

    return logs

def merge_daily_logs(daily_logs):

    merged_daily_logs = []

    for logs in daily_logs:

        for log in logs:

            merged_daily_logs.append(log)

    return merged_daily_logs


class WindowsUserReview:

    def __init__(self, review_date):
        if review_date is not None:
            self.review_date = datetime.strptime(review_date, '%Y-%m-%d')

    def getOperationLogs(self, logs_files):
        columns=[
                "Computer",
                "SystemTime",
                "TargetUserName",
                "TargetDomainName",
                "IpAddress",
                "LogonType",
                "ProcessName",
        ]
        daily_logs = get_daily_logs(logs_files)

        monthly_logs = merge_daily_logs(daily_logs)

        operation_logs = pd.DataFrame(monthly_logs, columns=columns)

        operation_logs['SystemTime'] = pd.to_datetime(operation_logs['SystemTime']).dt.date
        
        return operation_logs

    def getLastUserreview(self, filename):

        print("Reading previous user review file: {}".format(filename))

        p_user_review = pd.read_csv(filename, skip_blank_lines=True)

        p_user_review = p_user_review.drop(columns=[user_review_columns["domain"]])

        p_user_review.set_index([user_review_columns["username"]])

        return p_user_review

    def reviewAccountStatus(self, last_user_review, operation_logs):
        accounts_last_login_date = get_accounts_last_login_date(operation_logs)

        user_review = update_account_status(accounts_last_login_date, last_user_review, self.review_date)

        return user_review

    def reviewPasswordStatus(self, user_review, ad_filename):
        password_change_status = get_password_change_status(ad_filename)

        user_review = update_password_status(password_change_status, user_review, self.review_date)

        return user_review
