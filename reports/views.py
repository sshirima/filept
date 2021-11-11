from django.shortcuts import render
from reports.forms import ReportsForm, PRSReportForm
from reports.handles import create_epc_montly_reports, create_prs_reports

# Create your views here.

def reports(request):
    all_reports = [
        {'name':'epc','title':'EPC Reports', 'description':'Generate monthly EPC reports'},
        {'name':'services','title':'Services reports', 'description':'Generate monthly service application reports'},
    ]
    context = {
        'reports' : all_reports,
    }
    return render(request,'reports.html', context)


def reports_create(request, reportname):
    form = ReportsForm()
    context = {'reportname': reportname, 'form': form}

    if request.method == 'POST':

        if reportname == 'epc':
            form = ReportsForm(request.POST, request.FILES)

            if form.is_valid():
                files = request.FILES.getlist('input_files')
                exported_files = create_epc_montly_reports( _get_filepaths(files))
                context = {'create_success': True, 'reportname': reportname, 'exported_files': exported_files}
            else:
                context = {'create_fail':True, 'reportname': reportname,'form':form}
                

        if reportname == 'services':
            form = ReportsForm(request.POST, request.FILES)
            file_names = {}

            if form.is_valid():
                files = request.FILES.getlist('input_files')
                exported_files = create_prs_reports(_get_filepaths(files))
                context = {'create_success': True, 'reportname': reportname, 'exported_files': exported_files}
            else:
                context = {'create_fail':True,'reportname': reportname,'form':form}
            

    return render(request, 'reports_create.html', context)

def _get_filepaths(files):
    file_paths={}
    for f in files:
        file_paths[f.name] = f.temporary_file_path()
    return file_paths
