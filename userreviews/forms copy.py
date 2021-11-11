from django import forms
from django.core.validators import FileExtensionValidator

import csv

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


HEADERS = {
    'SAM Account Name': {'required':True},
    'Last Logon Time': {'required':True},
    'Full Name': {'required':False},
    'Email Address': {'required':False},
    'Manager': {'required':False},
    'Account Status': {'required':True},
    'When Created': {'required':False},
    'Password Status': {'required':True},
    'Department': {'required':False},
    'Mobile': {'required':False},
    'Company': {'required':False},
    'Password Expiry Date': {'required':False},
    'Days since password last set': {'required':False},
}

FILE_CHOICES =(
    ("file_one", "File one"),
    ("file_two", "File two"),
)

def ad_file_validator(document):
    # check file valid csv format
    validation_error_messages = []
    
    filesize = document.size
    
    if filesize > 10485760:
        raise ValidationError("The maximum file size that can be uploaded is 10MB")

    try:
        dialect = csv.Sniffer().sniff(document.read(1024).decode("utf-8"))
        document.seek(0, 0)
        
    except csv.Error:
        validation_error_messages.append(u'Not a valid CSV file')
        #raise ValidationError(u'Not a valid CSV file')

    reader = csv.reader(document.read().decode("utf-8").splitlines(), dialect)
    csv_headers = []
    required_headers = [header_name for header_name, values in
                        HEADERS.items() if values['required']]
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
        raise forms.ValidationError(" ".join(validation_error_messages))

    return True


class UploadFileForm(forms.Form):
    filename = forms.FileField(label='Filename',validators=[FileExtensionValidator(['csv']), ad_file_validator])
    choice_file = forms.ChoiceField(label= 'File choice',choices = FILE_CHOICES, required=True)

class SolarwindsForm(forms.Form):
    review_date = forms.DateTimeField(required=True, widget=forms.widgets.DateInput(attrs={'type': 'date', "class": "form-control",}))
    last_user_review = forms.FileField(label='Last User Review File',validators=[FileExtensionValidator(['csv'])])
    operation_logs = forms.FileField(label='Operation Logs File',validators=[FileExtensionValidator(['csv'])])
    active_directory_file = forms.FileField(label='Active Directory File',validators=[FileExtensionValidator(['csv'])])
