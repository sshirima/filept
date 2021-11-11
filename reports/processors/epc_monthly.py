import pandas as pd
from datetime import datetime
import pathlib

columns = {
    'start_time': 'Start Time',
    'ne_name': 'NE Name',
    'period': 'Period (min)',
    'whole_system': 'Whole System'
}

columns_ugw = {
    'throughput': 'Current UGW Throughput (kB/s)',
    'volume_down': 'GW outgoing downlink user traffic in KB (kB)',
    'volume_up': 'GW incoming uplink user traffic in KB (kB)',
    'pdp': 'Maximum simultaneously activated PDP contexts (number)',
    'dt': 'Current activated Direct Tunnel PDP contexts (number)'
}

columns_usn = {
    'volume_up_2g': 'Gn uplink traffic in MB of GERAN rat (MB)',
    'volume_down_2g': 'Gn downlink traffic in MB of GERAN rat (MB)',
    'volume_up_3g': 'Gn uplink traffic in MB of UTRAN rat (MB)',
    'volume_down_3g': 'Gn downlink traffic in MB of UTRAN rat (MB)',
    'volume_up_4g': 'SGi uplink user traffic in KB (kB)',
    'volume_down_4g': 'SGi downlink user traffic in KB (kB)',
    'throughput_up_2g': 'Gi downlink peak throughput  of GERAN rat in MB/s (MB/s)',
    'throughput_down_2g': 'Gi uplink peak throughput  of GERAN rat in MB/s (MB/s)',
    'throughput_up_3g': 'Gi downlink peak throughput  of UTRAN rat in MB/s (MB/s)',
    'throughput_down_3g': 'Gi uplink peak throughput  of UTRAN rat in MB/s (MB/s)',
    'throughput_up_4g': 'GTP based S5/S8 (SGW) downlink user traffic peak throughput in KB/s (kB/s)',
    'throughput_down_4g': 'GTP based S5/S8 (SGW) uplink user traffic peak throughput in KB/s (kB/s)',
    'sau_2g': 'Gb mode maximum attached users (number)',
    'sau_3g': 'Iu mode maximum attached users (number)',
    'sau_4g': 'Maximum attached users (number)',
    'pdp_2g': 'Gb mode maximum act PDP context (number)',
    'pdp_3g': 'Iu mode maximum active PDP context (number)',
    'pdp_4g': 'Maximum PDN connection number (number)',

}

def load_file_ugw_all(filename):

    performance_logs = pd.read_csv(
        filename.strip(), skip_blank_lines=True, header=5)

    performance_logs[columns['start_time']] = pd.to_datetime(
        performance_logs[columns['start_time']]).dt.date
    performance_logs[columns_ugw['throughput']] = pd.to_numeric(
        performance_logs[columns_ugw['throughput']])
    performance_logs[columns_ugw['volume_up']] = pd.to_numeric(performance_logs[columns_ugw['volume_up']])
    performance_logs[columns_ugw['volume_down']] = pd.to_numeric(performance_logs[columns_ugw['volume_down']])

    return performance_logs


def load_file_usn_sau_pdp(filename):

    performance_logs = pd.read_csv(
        filename.strip(), skip_blank_lines=True, header=5)

    performance_logs[columns['start_time']] = pd.to_datetime(
        performance_logs[columns['start_time']]).dt.date

    return performance_logs


def load_file_usn_volume_throughput(filename):

    performance_logs = pd.read_csv(
        filename.strip(), skip_blank_lines=True, header=5)

    performance_logs[columns['start_time']] = pd.to_datetime(
        performance_logs[columns['start_time']]).dt.date
    performance_logs[columns_usn['volume_up_2g']] = pd.to_numeric(
        performance_logs[columns_usn['volume_up_2g']])
    performance_logs[columns_usn['volume_down_2g']] = pd.to_numeric(
        performance_logs[columns_usn['volume_down_2g']])
    performance_logs[columns_usn['volume_up_3g']] = pd.to_numeric(
        performance_logs[columns_usn['volume_up_3g']])
    performance_logs[columns_usn['volume_down_3g']] = pd.to_numeric(
        performance_logs[columns_usn['volume_down_3g']])
    performance_logs[columns_usn['volume_up_4g']] = pd.to_numeric(
        performance_logs[columns_usn['volume_up_4g']])
    performance_logs[columns_usn['volume_down_4g']] = pd.to_numeric(
        performance_logs[columns_usn['volume_down_4g']])
    performance_logs[columns_usn['throughput_up_2g']] = pd.to_numeric(
        performance_logs[columns_usn['throughput_up_2g']])
    performance_logs[columns_usn['throughput_down_2g']] = pd.to_numeric(
        performance_logs[columns_usn['throughput_down_2g']])
    performance_logs[columns_usn['throughput_up_3g']] = pd.to_numeric(
        performance_logs[columns_usn['throughput_up_3g']])
    performance_logs[columns_usn['throughput_down_3g']] = pd.to_numeric(
        performance_logs[columns_usn['throughput_down_3g']])
    performance_logs[columns_usn['throughput_up_4g']] = pd.to_numeric(
        performance_logs[columns_usn['throughput_up_4g']])
    performance_logs[columns_usn['throughput_down_4g']] = pd.to_numeric(
        performance_logs[columns_usn['throughput_down_4g']])

    return performance_logs


def create_report_ugw_bynode(node_name, filename):

    performance_logs = load_file_ugw_all(filename)

    p_logs_bynode = performance_logs[performance_logs['NE Name'] == node_name]

    p_logs_bynode = p_logs_bynode.groupby(columns['start_time']).agg({columns_ugw['pdp']: ['max'],
                                                                      columns_ugw['dt']: ['max'],
                                                                      columns_ugw['throughput']: ['max'],
                                                                      columns_ugw['volume_up']: ['sum'],
                                                                      columns_ugw['volume_down']: ['sum']
                                                                      }).reset_index()
    p_logs_bynode.columns = p_logs_bynode.columns.get_level_values(0)

    p_logs_bynode[columns_ugw['throughput']
                  ] = p_logs_bynode[columns_ugw['throughput']]*8 / 1024 /1024
    p_logs_bynode[columns_ugw['volume_up']] = p_logs_bynode[columns_ugw['volume_up']] / 1024 / 1024
    p_logs_bynode[columns_ugw['volume_down']] = p_logs_bynode[columns_ugw['volume_down']] / 1024 / 1024

    p_logs_bynode['Volume'] = p_logs_bynode[columns_ugw['volume_up']] + p_logs_bynode[columns_ugw['volume_down']]

    p_logs_bynode = p_logs_bynode.astype(
        {columns_ugw['pdp']: 'int32'})
    p_logs_bynode = p_logs_bynode.astype(
        {columns_ugw['dt']: 'int32'})

    p_logs_bynode = p_logs_bynode.rename(columns={columns_ugw['pdp']: 'PDP_'+node_name,
                                         columns_ugw['dt']: 'DT_Tunnels_'+node_name,
                                         columns_ugw['throughput']: 'Throughput_'+node_name,
                                         'Volume': 'Volume_'+node_name})
    p_logs_bynode = p_logs_bynode.drop([columns_ugw['volume_up'],
                                        columns_ugw['volume_down'] ], axis=1)

    return p_logs_bynode


def create_report_usn_volume_throughput_bynode(node_name, filename):
    performance_logs = load_file_usn_volume_throughput(filename)
    p_logs_bynode = performance_logs[performance_logs[columns['ne_name']] == node_name]
    p_logs_bynode = p_logs_bynode.groupby(columns['start_time']).agg({columns_usn['volume_up_2g']: ['sum'],
                                                                      columns_usn['volume_down_2g']: ['sum'],
                                                                      columns_usn['volume_up_3g']: ['sum'],
                                                                      columns_usn['volume_down_3g']: ['sum'],
                                                                      columns_usn['volume_up_4g']: ['sum'],
                                                                      columns_usn['volume_down_4g']: ['sum'],
                                                                      columns_usn['throughput_up_2g']: ['max'],
                                                                      columns_usn['throughput_down_2g']: ['max'],
                                                                      columns_usn['throughput_up_3g']: ['max'],
                                                                      columns_usn['throughput_down_3g']: ['max'],
                                                                      columns_usn['throughput_up_4g']: ['max'],
                                                                      columns_usn['throughput_down_4g']: ['max']}).reset_index()
    p_logs_bynode.columns = p_logs_bynode.columns.get_level_values(0)

    p_logs_bynode[columns_usn['volume_up_2g']
                  ] = p_logs_bynode[columns_usn['volume_up_2g']] / 1024
    p_logs_bynode[columns_usn['volume_down_2g']
                  ] = p_logs_bynode[columns_usn['volume_down_2g']] / 1024
    p_logs_bynode[columns_usn['volume_up_3g']
                  ] = p_logs_bynode[columns_usn['volume_up_3g']] / 1024
    p_logs_bynode[columns_usn['volume_down_3g']
                  ] = p_logs_bynode[columns_usn['volume_down_3g']] / 1024
    p_logs_bynode[columns_usn['volume_up_4g']
                  ] = p_logs_bynode[columns_usn['volume_up_4g']] / 1024/1024
    p_logs_bynode[columns_usn['volume_down_4g']
                  ] = p_logs_bynode[columns_usn['volume_down_4g']] / 1024/1024
    p_logs_bynode[columns_usn['throughput_up_2g']
                  ] = p_logs_bynode[columns_usn['throughput_up_2g']]*8 / 1024
    p_logs_bynode[columns_usn['throughput_down_2g']
                  ] = p_logs_bynode[columns_usn['throughput_down_2g']]*8 / 1024
    p_logs_bynode[columns_usn['throughput_up_3g']
                  ] = p_logs_bynode[columns_usn['throughput_up_3g']]*8 / 1024
    p_logs_bynode[columns_usn['throughput_down_3g']
                  ] = p_logs_bynode[columns_usn['throughput_down_3g']]*8 / 1024
    p_logs_bynode[columns_usn['throughput_up_4g']
                  ] = p_logs_bynode[columns_usn['throughput_up_4g']]*8/1024 / 1024
    p_logs_bynode[columns_usn['throughput_down_4g']
                  ] = p_logs_bynode[columns_usn['throughput_down_4g']]*8/1024 / 1024

    p_logs_bynode['Volume_'+node_name+'_2G'] = p_logs_bynode[columns_usn['volume_up_2g']
                                                             ] + p_logs_bynode[columns_usn['volume_down_2g']]
    p_logs_bynode['Volume_'+node_name+'_3G'] = p_logs_bynode[columns_usn['volume_up_3g']
                                                             ] + p_logs_bynode[columns_usn['volume_down_3g']]
    p_logs_bynode['Volume_'+node_name+'_4G'] = p_logs_bynode[columns_usn['volume_up_4g']
                                                             ] + p_logs_bynode[columns_usn['volume_down_4g']]
    p_logs_bynode['Throughput_'+node_name+'_2G'] = p_logs_bynode[columns_usn['throughput_up_2g']
                                                                 ] + p_logs_bynode[columns_usn['throughput_down_2g']]
    p_logs_bynode['Throughput_'+node_name+'_3G'] = p_logs_bynode[columns_usn['throughput_up_3g']
                                                                 ] + p_logs_bynode[columns_usn['throughput_down_3g']]
    p_logs_bynode['Throughput_'+node_name+'_4G'] = p_logs_bynode[columns_usn['throughput_up_4g']
                                                                 ] + p_logs_bynode[columns_usn['throughput_down_4g']]

    p_logs_bynode = p_logs_bynode.drop([columns_usn['volume_up_2g'],
                                        columns_usn['volume_down_2g'],
                                        columns_usn['volume_up_3g'],
                                        columns_usn['volume_down_3g'],
                                        columns_usn['volume_up_4g'],
                                        columns_usn['volume_down_4g'],
                                        columns_usn['throughput_up_2g'],
                                        columns_usn['throughput_down_2g'],
                                        columns_usn['throughput_up_3g'],
                                        columns_usn['throughput_down_3g'],
                                        columns_usn['throughput_up_4g'],
                                        columns_usn['throughput_down_4g'], ], axis=1)
    return p_logs_bynode


def create_report_usn_sau_pdp_bynode(node_name, filename):

    sau_pdp_file = load_file_usn_sau_pdp(filename)

    p_logs_bynode = sau_pdp_file[sau_pdp_file[columns['ne_name']] == node_name]
    p_logs_bynode = p_logs_bynode.groupby(
        columns['start_time'], as_index=False).max()
    p_logs_bynode = p_logs_bynode.rename(columns={columns_usn['sau_2g']: 'SAU_'+node_name+'_2G',
                                         columns_usn['sau_3g']: 'SAU_'+node_name+'_3G',
                                         columns_usn['sau_4g']: 'SAU_'+node_name+'_4G',
                                         columns_usn['pdp_2g']: 'PDP_'+node_name+'_2G',
                                         columns_usn['pdp_3g']: 'PDP_'+node_name+'_3G',
                                         columns_usn['pdp_4g']: 'PDP_'+node_name+'_4G'})
    p_logs_bynode = p_logs_bynode.drop(
        [columns['period'], columns['ne_name'], columns['whole_system']], axis=1)
    return p_logs_bynode


class EPCMonthlyReports:

    def createUGWReport(self, filename):

        kwale_report = create_report_ugw_bynode('Kwale_UGW', filename)
        mbezi_report = create_report_ugw_bynode('Mbezi_UGW', filename)
    
        report = pd.merge(kwale_report, mbezi_report,
                          on=columns['start_time'], how='outer')
        report = report.reindex(sorted(report.columns), axis=1)
        report = report.set_index([columns['start_time']])
        print('Success: UGW report was created...')
        return report.transpose()

    def createUSNReport(self, filename_sau, filename_volume):
     
        kwale_report_sp = create_report_usn_sau_pdp_bynode('KwaleUSN9810', filename_sau)
        mbezi_report_sp = create_report_usn_sau_pdp_bynode('MbeziUS9810', filename_sau)

        kwale_report_vt = create_report_usn_volume_throughput_bynode('Kwale_UGW', filename_volume)
        mbezi_report_vt = create_report_usn_volume_throughput_bynode('Mbezi_UGW', filename_volume)

        report_sp = pd.merge(kwale_report_sp, mbezi_report_sp,
                            on=columns['start_time'], how='outer')
        report_vt = pd.merge(kwale_report_vt, mbezi_report_vt,
                            on=columns['start_time'], how='outer')

        report = pd.merge(report_sp, report_vt,
                        on=columns['start_time'], how='outer')

        report = report.reindex(sorted(report.columns), axis=1)
        report = report.set_index([columns['start_time']])
        print('Success: USN report was created...')
        return report.transpose()