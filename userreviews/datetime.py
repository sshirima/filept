

import dateutil.parser 
from datetime import datetime
from django.utils.timezone import make_aware
import xlrd

def get_datetime_from_string(date_string, format):
    try:
        return make_aware(datetime.strptime(date_string, format))
    except ValueError:
        return None

def get_datetime_no_format(date_string):
    date_format = "%Y-%m-%d %H:%M:%S"
    try:
        #Except axcel number date
        datetime_date = xlrd.xldate_as_datetime(float(date_string), 0)
        
        date_string = datetime_date.strftime(date_format)
        print('Date: {}'.format(date_string))

    except ValueError:
        pass

    try:
        #Except any string date
        d_util = dateutil.parser.parse(date_string)
        
        dateutil_string = d_util.strftime(date_format)
        return make_aware(datetime.strptime(dateutil_string, date_format))

    except TypeError as e:
        print('Error, {}'.format(str(e)))
        return None

    except dateutil.parser._parser.ParserError as e:
        print('Error, {}'.format(str(e)))
        return None

def convert_datetime_to_date(date_time, date_format="%Y-%m-%d"):
 
    date_string = date_time.strftime(date_format)
    return datetime.strptime(date_string, '%Y-%m-%d')