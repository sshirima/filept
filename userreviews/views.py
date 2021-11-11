from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from userreviews.forms import SolarwindsForm, CiscoISEForm, USNUGWForm, WindowsForm, DataImportForm
from userreviews.handles import create_solarwinds_userreview, create_ise_userreview, create_ugw_usn_userreview, create_windows_userreview, update_or_create_accounts_from_csv
import os
import mimetypes




def userreviews(request):
    all_nodes = [
        {'name':'usn_ugw','title':'UGW/USN', 'description':'Generate Huawei EPC user review'},
        {'name':'ise','title':'ISE', 'description':'Generate ISE user review for CDN nodes access'},
        {'name':'solarwinds','title':'Solarwinds', 'description':'Generate for Solarwinds NPM'},
        {'name':'windows','title':'Windows', 'description':'Generate Windows servers user review'},
    ]
    context = {
        'nodes' : all_nodes,
    }
    return render(request,'userreviews.html', context)


def userreviews_create(request, nodename):

    form = get_form(request, nodename)
    
    if request.method == 'GET':
        context = {'nodename':nodename, 'form': form}
        return render(request, 'userreviews_create.html', context)

    if request.method == 'POST':

        form = get_form(request, nodename)

        if form.is_valid():
            files = {}
            if nodename == 'solarwinds':
                date = form.cleaned_data['review_date']
                files['last_user_review_file'] = form.cleaned_data['last_user_review_file'].temporary_file_path()
                files['operation_logs_file'] = form.cleaned_data['operation_logs_file'].temporary_file_path()
                files['active_directory_file'] = form.cleaned_data['active_directory_file'].temporary_file_path()
                exported_files = create_solarwinds_userreview(date, files)
                context = {'create_success': True, 'nodename': nodename, 'exported_files':exported_files}

            if nodename == 'ise':
                date = '2021-09-30'#form.cleaned_data['review_date']
                files['last_user_review_file'] = 'media/imports/user_review.csv'#form.cleaned_data['last_user_review_file'].temporary_file_path()
                files['operation_logs_file'] = 'media/imports/ise_dump_09.csv'#form.cleaned_data['operation_logs_file'].temporary_file_path()
                files['active_directory_file'] = 'media/imports/ad_dump_07.csv'#form.cleaned_data['active_directory_file'].temporary_file_path()
                exported_files = create_ise_userreview(date, files)

                context = {'create_success': True, 'nodename': nodename, 'exported_files':exported_files}

            if nodename == 'usn_ugw':
                date = '2021-09-30'#form.cleaned_data['review_date']
                files['operation_logs_file'] = form.cleaned_data['operation_logs_file'].temporary_file_path()
                exported_files = create_ugw_usn_userreview(date, files)
                context = {'create_success': True, 'nodename': nodename, 'exported_files':exported_files}

            if nodename == 'windows':
                date = '2021-11-04'#form.cleaned_data['review_date']
                
                files['last_user_review_file'] = form.cleaned_data['last_user_review_file'].temporary_file_path()
                files['operation_logs_file'] = _get_temporary_file_path(request.FILES.getlist('operation_logs_file'))
                files['active_directory_file'] = form.cleaned_data['active_directory_file'].temporary_file_path()
                exported_files = create_windows_userreview(date, files)
                context = {'create_success': True, 'nodename': nodename, 'exported_files':exported_files}
        else:
            context = {'nodename': nodename,'form':form}

        return render(request, 'userreviews_create.html', context)


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
    return render(request, 'data_import.html')


def data_import_create(request):
    form = DataImportForm()
    context = {'form': form}

    if request.method == 'POST':

        form = DataImportForm(request.POST, request.FILES)

        if form.is_valid():
            file_path = form.cleaned_data['input_file'].temporary_file_path()
            accounts = update_or_create_accounts_from_csv(file_path, 'AD')
            context = {'create_success': True}
        else:
            context = {'create_fail':True}
                
    return render(request, 'data_import_create.html', context)


def get_form(request, nodename):
    if request.method == 'GET':
        if nodename == 'solarwinds':
            return SolarwindsForm()

        if nodename == 'ise':
            return CiscoISEForm()

        if nodename == 'usn_ugw':
            return USNUGWForm()

        if nodename == 'windows':
            return WindowsForm()
        return None

    if request.method == 'POST':
        if nodename == 'solarwinds':
            return SolarwindsForm(request.POST, request.FILES)
        
        if nodename == 'ise':
            return CiscoISEForm(request.POST, request.FILES)
        
        if nodename == 'usn_ugw':
            return USNUGWForm(request.POST, request.FILES)

        if nodename == 'windows':
            return WindowsForm(request.POST, request.FILES)
        return None

def _get_temporary_file_path(files):
    file_paths=[]
    for f in files:
        file_paths.append(f.temporary_file_path())
    return file_paths