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
    #Database access
    lastUserReview = solarwindsUserReview.getLastUserreview(files['last_user_review_file'])#This will be removed
    userReview = solarwindsUserReview.reviewAccountStatus(lastUserReview, operationLogs)
    userReview = solarwindsUserReview.reviewPasswordStatus(userReview, files['active_directory_file'])#This will be removed
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

    
def get_filename(name ):
    return 'media/imports/{}.csv'.format(name.upper())