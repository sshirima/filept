import pandas as pd
import xml.etree.ElementTree as Xet

COLUMNS_LOGS = {
    'username':'username',
    'last_logon':'last_logon',
    'account_type':'account_type'
}

def parse_solarwinds_logs(filename):
    columns_logs = {
        'name':'NAME',
        'last_login':'LAST LOGIN',
        'account_type':'ACCOUNT TYPE',

    }
    operation_logs = pd.read_csv(filename.strip(), skip_blank_lines=True)
    
    #Convert to proper data format
    operation_logs[columns_logs['name']] = operation_logs[columns_logs['name']].str.replace('VCTZ\\', '', regex=False)
    operation_logs.loc[operation_logs[columns_logs['account_type']] == 'Local Orion', columns_logs['account_type']] = 'local'
    operation_logs.loc[operation_logs[columns_logs['account_type']] == 'AD Individual', columns_logs['account_type']] = 'active_directory'
    
    operation_logs[columns_logs['last_login']] = pd.to_datetime(operation_logs[columns_logs['last_login']]).dt.date
    
    #Select files to return
    operation_logs = operation_logs[[columns_logs['name'], columns_logs['last_login'], columns_logs['account_type']]]
    
    #rename the columns
    operation_logs = operation_logs.rename(
        columns={
            columns_logs['name']: COLUMNS_LOGS['username'], 
            columns_logs['last_login']: COLUMNS_LOGS['last_logon'],
            columns_logs['account_type']: COLUMNS_LOGS['account_type'],
        })

    
    return operation_logs

def parse_cisco_ise_logs(filename):
    print('Reading ise logs file: {}'.format(filename))

    columns_logs= {
        'logged_time' : 'LOGGED_TIME',
        'username':'USERNAME',
        'authentication_policy':'AUTHENTICATION_POLICY'
    }

    ise_ad_policies=['CORE_POLICY >> Default','RAN_PE_POLICY >> Default','RAN_POLICY >> Default', 'E_PE_POLICY >> Default','FIREWALL_POLICY >> Default']
    ise_local_policies=['RAN_POLICY >> SCM_AUTH', 'FIREWALL_POLICY >> TUFIN']
    
    operation_logs = pd.read_csv(filename.strip(), skip_blank_lines=True)
    operation_logs = operation_logs.rename(columns=lambda x: x.replace("'","").replace('"','')).replace(" ","")
    operation_logs = operation_logs[[columns_logs['logged_time'], columns_logs['username'], columns_logs['authentication_policy']]]
    operation_logs[columns_logs['logged_time']] = pd.to_datetime(operation_logs[columns_logs['logged_time']]).dt.date

    #Get accounts last logins
    account_last_logins = operation_logs[[columns_logs['username'], columns_logs['logged_time'], columns_logs['authentication_policy']]].sort_values(
            by=[columns_logs['username'], columns_logs['logged_time']]).groupby(columns_logs['username'], as_index=False).last()

    account_last_logins[columns_logs['username']] = account_last_logins[columns_logs['username']].str.replace("'","")
    account_last_logins[columns_logs['authentication_policy']] = account_last_logins[columns_logs['authentication_policy']].str.replace("'","")

    account_last_logins.loc[account_last_logins[columns_logs['authentication_policy']].isin(ise_ad_policies), columns_logs['authentication_policy']] = 'active_directory'
    account_last_logins.loc[account_last_logins[columns_logs['authentication_policy']].isin(ise_local_policies), columns_logs['authentication_policy']] = 'local'
    
    account_last_logins.set_index([columns_logs['username']])

    account_last_logins = account_last_logins.rename(
        columns={
            columns_logs['username']: COLUMNS_LOGS['username'], 
            columns_logs['logged_time']: COLUMNS_LOGS['last_logon'],
            columns_logs['authentication_policy']: COLUMNS_LOGS['account_type'],
        })
    return account_last_logins




def parse_epc_logs(filename, system_name):
    columns_logs = {
            'start_time':'Start Time',
            'user':'User',
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
    print('Reading epc logs file: {}'.format(filename))

    operation_logs = pd.read_csv(filename.strip(), skip_blank_lines=True, header=5)
    operation_logs[columns_logs['start_time']] = pd.to_datetime(operation_logs[columns_logs['start_time']]).dt.date

    #Get accounts last logins
    if system_name in ['MbeziUS9810','KwaleUSN9810']:

        operation_logs[columns_logs[columns_logs['user']]] = operation_logs[columns_logs[columns_logs['user']]].str.replace('EMS\\', '', regex=False)

        account_last_logins = operation_logs[(operation_logs[columns_logs['ne_name']].str.contains(system_name)) & (operation_logs[columns_logs['result']] == 'Succeeded')]

    else:
        account_last_logins = operation_logs[(operation_logs[columns_logs['ne_name']].str.contains(system_name)) & (
        operation_logs[columns_logs['command']].str.contains('LGI REQUEST')) & (operation_logs[columns_logs['result']] == 'Succeeded')]

    account_last_logins_sorted = account_last_logins[[columns_logs['user'], columns_logs['start_time']]].sort_values(
        by=[columns_logs['user'], columns_logs['start_time']]).groupby(columns_logs['user'], as_index=False).last()

    account_last_logins_sorted.set_index([columns_logs['user']])

    account_last_logins_sorted[COLUMNS_LOGS['account_type']] = 'local'

    account_last_logins_sorted = account_last_logins_sorted.rename(
        columns={
            columns_logs['user']: COLUMNS_LOGS['username'], 
            columns_logs['start_time']: COLUMNS_LOGS['last_logon'],
        })

    return account_last_logins_sorted

def parse_windows_logs(files, system_name=''):
    operation_logs = parse_windows_xml_files(files)

    remote_desktop_logs = operation_logs[(operation_logs['LogonType'] == '10')][['TargetUserName', 'SystemTime', 'TargetDomainName']]

    remote_desktop_logs = (
        remote_desktop_logs.sort_values(by=['TargetUserName', 'SystemTime'])
        .groupby('TargetUserName', as_index=False)
        .last()
    )

    remote_desktop_logs = remote_desktop_logs.rename(
        columns={
            'TargetUserName': COLUMNS_LOGS['username'], 
            'SystemTime': COLUMNS_LOGS['last_logon'],
            'TargetDomainName': COLUMNS_LOGS['account_type'],
        })

    remote_desktop_logs.set_index(COLUMNS_LOGS['username'])
    remote_desktop_logs.loc[remote_desktop_logs[COLUMNS_LOGS['account_type']] == system_name, COLUMNS_LOGS['account_type']] = 'local'
    remote_desktop_logs.loc[remote_desktop_logs[COLUMNS_LOGS['account_type']] == 'VCTZ', COLUMNS_LOGS['account_type']] = 'active_directory'

    return remote_desktop_logs

def parse_windows_xml_files(logs_files):
    columns=[
            "Computer",
            "SystemTime",
            "TargetUserName",
            "TargetDomainName",
            "IpAddress",
            "LogonType",
            "ProcessName",
    ]
    daily_logs = parse_daily_xml_files(logs_files)

    monthly_logs = merge_daily_logs(daily_logs)

    operation_logs = pd.DataFrame(monthly_logs, columns=columns)

    operation_logs['SystemTime'] = pd.to_datetime(operation_logs['SystemTime']).dt.date
    
    return operation_logs


def parse_daily_xml_files(logs_files):

    logs = []

    for log_file in logs_files:

        d_logs = parse_xml_file(log_file)

        logs.append(d_logs)

    return logs

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


def merge_daily_logs(daily_logs):

    merged_daily_logs = []

    for logs in daily_logs:

        for log in logs:

            merged_daily_logs.append(log)

    return merged_daily_logs
