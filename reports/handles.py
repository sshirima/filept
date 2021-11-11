from reports.processors.epc_monthly import EPCMonthlyReports
from reports.processors.prs_reports import PRSReport
from userreviews.files import save_data_to_csv

default_names = {
    'ugw':'Monthly_UGW_PDP_DT_Throughput_Volume.csv',
    'usn_sau':'Monthly_USN_SAU_PDP_GB_IU_S1.csv',
    'usn_traffic':'Monthly_USN_VOLUME_THROUGHPUT.csv',

    'youtube_file':'By Application for Service_Youtube_Total Bandwidth by Application.csv',
    'netflix_file':'By Application for Service_Netflix_Total Bandwidth by Application.csv',
    'voip_file':'By Application for Service_VoIP_Total Bandwidth by Category.csv',
    'game_file':'By Application for Service_Game_Total Bandwidth by Category.csv',
    'im_file':'By Application for Service_IM_Total Bandwidth by Category.csv',
    'p2p_file':'By Application for Service_P2P_Total Bandwidth by Category.csv',
    'filetransfer_file':'By Application for Service_File_Access_Total Bandwidth by Category.csv',
    'streaming_file':'By Application for Service_Streaming_Total Bandwidth by Category.csv',
    'mail_file':'By Application for Service_Email_Total Bandwidth by Category.csv',
    'webapp_file':'By Application for Service_Web_Browsing_Total Bandwidth by Category.csv',
}

def create_epc_montly_reports(files):
    saved_files = []
    reportCreator = EPCMonthlyReports()

    reportUGW = reportCreator.createUGWReport(files[default_names['ugw']])
    ugw_saved_file = save_data_to_csv(reportUGW, 'UGW')
    saved_files.append(ugw_saved_file)

    reportUSN = reportCreator.createUSNReport(files[default_names['usn_sau']], files[default_names['usn_traffic']])
    usn_saved_file = save_data_to_csv(reportUSN, 'USN')
    saved_files.append(usn_saved_file)
   
    return saved_files


def create_prs_reports(files):
    saved_files = []
    reportCreator = PRSReport()

    streaming_files = {
        'youtube_file':files[default_names['youtube_file']],
        'netflix_file':files[default_names['netflix_file']],
    }
    streamingReport = reportCreator.createYoutubeNetflixReport(streaming_files)
    streaming_saved_file = save_data_to_csv(streamingReport, 'Youtube_Netflix')
    saved_files.append(streaming_saved_file)

    services_files = {
        'voip_file':files[default_names['voip_file']],
        'game_file':files[default_names['game_file']],
        'im_file':files[default_names['im_file']],
        'p2p_file':files[default_names['p2p_file']],
        'filetransfer_file':files[default_names['filetransfer_file']],
        'streaming_file':files[default_names['streaming_file']],
        'mail_file':files[default_names['mail_file']],
        'webapp_file':files[default_names['webapp_file']],
    }
    servicesReport = reportCreator.createServiceReport(services_files)
    services_saved_file = save_data_to_csv(streamingReport, 'Services')
    saved_files.append(services_saved_file)

    return saved_files


