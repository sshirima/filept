import csv
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class CsvFileValidator (object):
    def __init__(self, csv_headers={}, message=None, code=None):
        self.csv_headers = csv_headers
        

    def __call__(self, document):
        validation_error_messages = []

        #filesize = document.size
        #if filesize > 10485760:
        #    raise ValidationError("The maximum file size that can be uploaded is 10MB")

        try:
            dialect = csv.Sniffer().sniff(document.read(1024).decode("utf-8"))
            
        except csv.Error as e:
            dialect = 'excel'
            print('Error, {}'.format(str(e)))
            #validation_error_messages.append(u'Not a valid CSV file')
        document.seek(0, 0)
        if self.csv_headers and not validation_error_messages:
            reader = csv.reader(document.read().decode("utf-8").splitlines(), dialect=dialect)
            csv_headers = []
            required_headers = [header_name for header_name, values in self.csv_headers.items() if values['required']]
            for y_index, row in enumerate(reader):
                # check that all headers are present
                if y_index == 0:
                    # store header_names to sanity check required cells later
                    csv_headers = [header_name for header_name in row if header_name] 
                    missing_headers = set(required_headers) - set([r for r in row])
                    if missing_headers:
                        missing_headers_str = ', '.join(missing_headers)
                        validation_error_messages.append(u'Missing required headers: %s' % (missing_headers_str))
                        #raise ValidationError(u'Missing headers: %s' % (missing_headers_str))
                    continue
                # ignore blank rows
                if not ''.join(str(x) for x in row):
                    continue
                # sanity check required cell values
                for x_index, cell_value in enumerate(row):
                    # if indexerror, probably an empty cell past the headers col count
                    try:
                        csv_headers[x_index]
                    except IndexError:
                        continue
                    if csv_headers[x_index] in required_headers:
                        if not cell_value:
                            validation_error_messages.append(u'Missing required value %s for row %s' %
                                                    (csv_headers[x_index], y_index + 1))
                            #raise ValidationError(u'Missing required value %s for row %s' %(csv_headers[x_index], y_index + 1))

        if validation_error_messages:
            raise ValidationError(" ".join(validation_error_messages))
            