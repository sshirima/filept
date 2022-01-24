from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from userreviews.forms import SolarwindsForm, CiscoISEForm, USNUGWForm, WindowsForm, DataImportForm
import userreviews.forms as u_form
import userreviews.services as u_service
from userreviews.handlers import create_solarwinds_userreview, create_ise_userreview, create_ugw_usn_userreview, create_windows_userreview
import os
import mimetypes




def userreviews(request):
    systems = [
        
        {'name':'solarwinds','title':'Solarwinds', 'description':'Parse logs for Solarwinds NPM server'},
        {'name':'ise','title':'Cisco ISE', 'description':'Parse logs For Identity Service Engine'},
        {'name':'Kwale_UGW','title':'Kwale UGW', 'description':'Parse logs For Kwale UGW'},
        {'name':'Mbezi_UGW','title':'Mbezi UGW', 'description':'Parse logs For Mbezi UGW'},
        {'name':'MbeziUS9810','title':'Mbezi USN', 'description':'Parse logs For Mbezi USN'},
        {'name':'KwaleUSN9810','title':'Kwale USN', 'description':'Parse logs For Kwale USN'},
        {'name':'WIN-Q5K8NDDGDGH','title':'Windows Solarwinds', 'description':'Parse logs For windows server'},
    ]
    context = {
        'systems' : systems,
    }
    return render(request,'userreviews.html', context)

def upload_system_logs(request, system_name):
    form = select_upload_log_form(request, system_name)
    context = {'form': form, 'system_name':system_name}

    if request.method == 'POST':

        form = select_upload_log_form(request, system_name)
        context['form'] = form

        if form.is_valid():
            if system_name in ['WIN-Q5K8NDDGDGH']:
                log_file_path = _get_temporary_file_path(request.FILES.getlist('log_file')) 
            else:
                log_file_path = form.cleaned_data['log_file'].temporary_file_path() 

            operation_logs = u_service.parse_system_logs(system_name, log_file_path)
            system_accounts = u_service.update_system_accounts(system_name, operation_logs, form.cleaned_data['review_date'])
            context['data'] = system_accounts
            context['success'] = True

        else: 
            print('Form not valid')

    return render(request, 'upload_system_logs.html', context)


def select_upload_log_form(request, system_name):

    if request.method == 'GET':
        if system_name in ['solarwinds','ise','Kwale_UGW', 'Mbezi_UGW', 'KwaleUSN9810', 'MbeziUS9810']:
            return u_form.UploadLogsForm()
        else:
            return u_form.UploadLogsWindowsForm()

    if request.method == 'POST':
        if system_name in ['solarwinds','ise','Kwale_UGW', 'Mbezi_UGW', 'KwaleUSN9810', 'MbeziUS9810']:
            return u_form.UploadLogsForm(request.POST, request.FILES)
        else:
            return u_form.UploadLogsWindowsForm(request.POST, request.FILES)


def download_file(request, filename):
    #fill these variables with real values
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = BASE_DIR + '/media/export/' + filename
    fl = open(filepath, 'r')
    mime_type, _ = mimetypes.guess_type(filepath)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


def data_import(request):
    systems = [
        {'name':'active_directory','title':'Active Directory', 'description':'Import dump file for AD'},
        {'name':'ise','title':'ISE', 'description':'Generate ISE user review for CDN nodes access'},
        {'name':'solarwinds','title':'Solarwinds', 'description':'Generate for Solarwinds NPM'},
        {'name':'Kwale_UGW','title':'Kwale UGW', 'description':'Kwale UGW'},
        {'name':'Mbezi_UGW','title':'Mbezi UGW', 'description':'Mbezi UGW'},
        {'name':'KwaleUSN9810','title':'Kwale USN', 'description':'Kwale USN'},
        {'name':'MbeziUS9810','title':'Mbezi USN', 'description':'Mbezi USN'},
    ]

    context = {
        'systems' : systems,
    }
    return render(request, 'data_import.html', context)


def data_import_create(request, system_name):

    form = select_import_data_form(request, system_name)
    context = {'form': form, 'system_name':system_name}

    if request.method == 'POST':

        form = select_import_data_form(request, system_name)

        if form.is_valid():
            
            if system_name == 'active_directory':
                ad_temp_file_path = form.cleaned_data['input_file'].temporary_file_path() 
                context['data'] = u_service.import_ad_data_from_csv(ad_temp_file_path, u_service.columns_ad)
                context['success'] = True

            else:
                ur_temp_file_path = form.cleaned_data['input_file'].temporary_file_path() 
                context['data'] = u_service.import_system_data_from_csv(ur_temp_file_path, u_service.columns_ur, system_name=system_name)
                context['success'] = True

        else:
            print('Errors, Form is invalid')
            context['form'] = form


                
    return render(request, 'data_import_create.html', context)


def select_import_data_form(request, system_name):
    if request.method == 'GET':
        if system_name == 'active_directory':
            return u_form.ImportAdDataForm()
        else:
            return u_form.ImportUserreviewDataForm()

    if request.method == 'POST':
        if system_name == 'active_directory':
            return u_form.ImportAdDataForm(request.POST, request.FILES)
        else:
            return u_form.ImportUserreviewDataForm(request.POST, request.FILES)
    

def _get_temporary_file_path(files):
    file_paths=[]
    for f in files:
        file_paths.append(f.temporary_file_path())
    return file_paths


from django.views.generic import ListView
from django_tables2 import SingleTableView
import userreviews.models as ur_models
import userreviews.tables as ur_tables
import userreviews.filters as ur_filters

from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from django_tables2 import RequestConfig

class SystemAccountListView(SingleTableMixin, FilterView):
    model = ur_models.SystemAccount
    table_class = ur_tables.SystemAccountTable
    table_data = ur_models.SystemAccount.objects.filter(system__name = 'ise')
    template_name = 'accounts.html'
    paginate_by = 10
    filterset_class = ur_filters.SystemAccountsFilter
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = super(SystemAccountListView, self).get_queryset()
        self.filter = self.filterset_class(self.request.GET, queryset=qs)
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super(SystemAccountListView, self).get_context_data()
        filter = ur_filters.SystemAccountsFilter(self.request.GET, queryset=self.get_queryset(**kwargs))
        table = ur_tables.SystemAccountTable(filter.qs)
        RequestConfig(self.request).configure(table)
        context['filter'] = filter
        context['table'] = table
        return context
