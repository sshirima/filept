from django import forms
from django.core.validators import FileExtensionValidator
from userreviews.validators import CsvFileValidator
from django.conf import settings
import datetime

class SolarwindsForm(forms.Form):
    review_date = forms.DateTimeField(initial=datetime.date.today, required=True, widget=forms.widgets.DateInput(attrs={'type': 'date', "class": "form-control",}))
    last_user_review_file = forms.FileField(validators=[FileExtensionValidator(['csv']), CsvFileValidator({})])
    operation_logs_file = forms.FileField(validators=[FileExtensionValidator(['csv']), CsvFileValidator({})])
    active_directory_file = forms.FileField(validators=[FileExtensionValidator(['csv']), CsvFileValidator(settings.CSV_HEADERS['ad_file'])])

class CiscoISEForm(forms.Form):
    review_date = forms.DateTimeField(initial=datetime.date.today, required=True, widget=forms.widgets.DateInput(attrs={'type': 'date', "class": "form-control",}))
    last_user_review_file = forms.FileField(validators=[FileExtensionValidator(['csv']), CsvFileValidator({})])
    active_directory_file = forms.FileField(validators=[FileExtensionValidator(['csv']), CsvFileValidator(settings.CSV_HEADERS['ad_file'])])


class USNUGWForm(forms.Form):
    review_date = forms.DateTimeField(initial=datetime.date.today, required=True, widget=forms.widgets.DateInput(attrs={'type': 'date', "class": "form-control",}))
    operation_logs_file = forms.FileField(validators=[FileExtensionValidator(['csv']), CsvFileValidator({})])

class WindowsForm(forms.Form):
    review_date = forms.DateTimeField(initial=datetime.date.today, required=True, widget=forms.widgets.DateInput(attrs={'type': 'date', "class": "form-control",}))
    last_user_review_file = forms.FileField(validators=[FileExtensionValidator(['csv']), CsvFileValidator({})])
    operation_logs_file = forms.FileField(validators=[FileExtensionValidator(['xml'])], 
                                            widget=forms.ClearableFileInput(attrs={'multiple': True}))
    active_directory_file = forms.FileField(validators=[FileExtensionValidator(['csv']), CsvFileValidator(settings.CSV_HEADERS['ad_file'])])

class DataImportForm(forms.Form):
    input_file = forms.FileField(validators=[FileExtensionValidator(['csv']), CsvFileValidator({})])