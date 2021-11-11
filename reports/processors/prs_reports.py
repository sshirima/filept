import pandas as pd
from datetime import datetime

def get_filename(keyword):
    now = datetime.now()

    return 'exports/{}_{}_{}_{}_{}.csv'.format(now.year, now.month, now.day, str(
            now.hour)+str(now.minute)+str(now.second), keyword)

def read_input_file_csv(filename):
    data_file = pd.read_csv(filename, skip_blank_lines=True)
    data_file['Total Traffic (MB)'] = data_file['Total Traffic (MB)'].str.replace(',','')
    data_file['Total Traffic (MB)'] = pd.to_numeric(data_file['Total Traffic (MB)'])
    return data_file


def create_dataframe_report(data_file, service_type):
    report = pd.DataFrame()
    report['Time'] = pd.to_datetime(data_file['Time']).dt.date
    report['Service'] = service_type
    report['Total'] = data_file['Total Traffic (MB)'] / 1024 / 1024
    return report

class PRSReport :

    def createYoutubeNetflixReport(self, files):
        #read CSV files for youtube and netflix
        youtube_file = read_input_file_csv(files['youtube_file']) #read_input_file_csv('files/By Application for Service_Youtube_Total Bandwidth by Application.csv')
        netflix_file = read_input_file_csv(files['netflix_file'])#read_input_file_csv('files/By Application for Service_Netflix_Total Bandwidth by Application.csv')

        #Create dataframe report
        report = pd.DataFrame()
        report['Time'] = youtube_file['Time']
        report['Youtube'] = youtube_file['Total Traffic (MB)'] / 1024 / 1024
        report['Netflix'] = netflix_file['Total Traffic (MB)'] / 1024 / 1024

        print('Success: Youtube report created')
        return report

    def createServiceReport(self, files):
        #Read csv files for voip
        voip_file = read_input_file_csv(files['voip_file'])#read_input_file_csv('files/By Application for Service_VoIP_Total Bandwidth by Category.csv')
        game_file =  read_input_file_csv(files['game_file'])#read_input_file_csv('files/By Application for Service_Game_Total Bandwidth by Category.csv')
        im_file =  read_input_file_csv(files['im_file'])#read_input_file_csv('files/By Application for Service_IM_Total Bandwidth by Category.csv')
        p2p_file =  read_input_file_csv(files['p2p_file'])#read_input_file_csv('files/By Application for Service_P2P_Total Bandwidth by Category.csv')
        filetransfer_file =  read_input_file_csv(files['filetransfer_file'])#read_input_file_csv('files/By Application for Service_File_Access_Total Bandwidth by Category.csv')
        streaming_file =  read_input_file_csv(files['streaming_file'])#read_input_file_csv('files/By Application for Service_Streaming_Total Bandwidth by Category.csv')
        mail_file =  read_input_file_csv(files['mail_file'])#read_input_file_csv('files/By Application for Service_Email_Total Bandwidth by Category.csv')
        webapp_file =  read_input_file_csv(files['webapp_file'])#read_input_file_csv('files/By Application for Service_Web_Browsing_Total Bandwidth by Category.csv')

        #Create dataframe report
        report = pd.DataFrame()
        report = create_dataframe_report(voip_file, 'VoIP')
        report = report.append(create_dataframe_report(game_file, 'Gaming'))
        report = report.append(create_dataframe_report(im_file, 'Instant Messaging Apps'))
        report = report.append(create_dataframe_report(p2p_file, 'P2P Apps'))
        report = report.append(create_dataframe_report(filetransfer_file, 'File transfer'))
        report = report.append(create_dataframe_report(streaming_file, 'Streaming'))
        report = report.append(create_dataframe_report(mail_file, 'Mail'))
        report = report.append(create_dataframe_report(webapp_file, 'Web Apps'))

        report = report.sort_values(by=['Time'])

        print('Success: Application services reports created')
        return report
        