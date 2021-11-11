from django import forms
from django.core.validators import FileExtensionValidator
from userreviews.validators import CsvFileValidator
from django.conf import settings

class ReportsForm(forms.Form):
    input_files = forms.FileField(validators=[FileExtensionValidator(['csv']), CsvFileValidator({})], 
                                    widget=forms.ClearableFileInput(attrs={'multiple': True}))

class PRSReportForm(forms.Form):
    youtube_netflix_files = forms.FileField(validators=[FileExtensionValidator(['csv']), CsvFileValidator({})], 
                                    widget=forms.ClearableFileInput(attrs={'multiple': True}))
    service_app_files = forms.FileField(validators=[FileExtensionValidator(['csv']), CsvFileValidator({})], 
                                    widget=forms.ClearableFileInput(attrs={'multiple': True}))