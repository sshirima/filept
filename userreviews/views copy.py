from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from userreviews.forms import UserReviewForm, UploadFileForm
from django.urls import reverse
import pandas as pd

#To be moved to service layer
from userreviews.processors.solarwinds import SolarwindsUserReview

# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def home(request):
    return render(request,'home.html', {})


def nodes_index(request):
    all_nodes = [
        {'name':'usn_ugw','title':'UGW/USN', 'description':'Generate Huawei EPC user review'},
        {'name':'ise','title':'ISE', 'description':'Generate ISE user review for CDN nodes access'},
        {'name':'solarwinds','title':'Solarwinds', 'description':'Generate for Solarwinds NPM'},
        {'name':'windows','title':'Windows', 'description':'Generate Windows servers user review'},
    ]

    context = {
        'nodes' : all_nodes,
    }
    return render(request,'nodes_index.html', context)


def user_review_generate(request, node_name):

    is_posted = request.method == 'POST'

    if node_name == 'usn_ugw':
        data = ''

    form = UserReviewForm()

    if is_posted:
        form = UserReviewForm(request.POST, request.FILES)
        if form.is_valid():
            params = {
                'review_date':form.cleaned_data['review_date'],
                'last_user_review':form.cleaned_data['last_user_review'],
            }

            print('Params:{}'.format(params))

            return render(request,'user_review.html',{'is_posted': is_posted, 'params':params})
            #Do user review
        else:
            print('Form not valid')
    context = {
        'is_posted': is_posted,
        'node_name': node_name,
        #'form': form,
    }

    if node_name == 'solarwinds':

        solarwindsUserReview = SolarwindsUserReview(review_date='2021-09-30')
    
        operationLogs = solarwindsUserReview.getOperationLogs('media/logs/solarwinds_logs.csv')
    
        lastUserReview = solarwindsUserReview.getLastUserreview('media/reviews/user_review_solarwinds_kwale.csv')
    
        userReview = solarwindsUserReview.reviewAccountStatus(lastUserReview, operationLogs)
    
        userReview = solarwindsUserReview.reviewPasswordStatus(userReview, 'media/ad/ad_dump_10.csv')
    
    return render(request,'user_review.html', context)


def reports_index(request):
    all_reports = [
        {'name':'prs','title':'PRS service reports', 'description':'Monthly service reports from PRS'},
        {'name':'u2020','title':'EPC usage reports', 'description':'Monthly usage reports from U2020'},
    ]

    context = {
        'reports' : all_reports,
    }
    return render(request,'reports_index.html', context)


def data_update(request):
    all_nodes = [
        {'name':'usn_ugw','title':'UGW/USN', 'description':'Load user account data for EPC nodes'},
        {'name':'ad','title':'Active Directory', 'description':'Load user account data for Active Directory'},
        {'name':'windows','title':'Windows', 'description':'Load user account data for Windows'},
    ]

    context = {
        'nodes':all_nodes
    }
    return render(request,'data_update.html', context)


def data_upload(request, node_name):
    is_post_success = False

    context ={
        'node_name':node_name,
        'is_post_success': False
    }

    form = UploadFileForm()

    if request.method == 'POST':

        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            #Validate columns

            handle_uploaded_file(request.FILES['filename'])
            #return HttpResponseRedirect(reverse("data-upload"))
            context['is_post_success'] = True

            return render(request, 'data_upload.html', context)

    return render(request, 'data_upload.html', {'node_name':node_name, 'form': form})


from django.db import transaction
from userreviews.models import Account
import csv
from datetime import datetime
from django.utils.timezone import make_aware

def handle_uploaded_file(f):

    file_path = 'media/tmp/{}'.format(f.name)

    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    update_or_create_accounts_from_csv(file_path, 'AD')



def update_or_create_accounts_from_csv(filepath, auth_type):
    account_models = []
    with transaction.atomic():
        with open(filepath) as csvfile:
            accounts = csv.DictReader(csvfile)
            for account in accounts:
                try:
                    account_values = {  'fullname': account[cols['fullname']],
                                        'email': account[cols['email']],
                                        'mobile_phone': account[cols['mobile_phone']],
                                        'company': account[cols['company']],
                                        'department': account[cols['department']],
                                        'manager': account[cols['manager']],
                                        'auth_type': auth_type,
                                        'date_created':get_datetime_from_string(account[cols['date_created']], "%m/%d/%Y %H:%M:%S"),
                                        'date_last_logon':get_datetime_from_string(account[cols['date_last_logon']], "%m/%d/%Y %H:%M:%S"),
                                        'date_password_expiry':get_datetime_from_string(account[cols['date_password_expiry']], "%m/%d/%Y %H:%M:%S"),
                                        'password_status': account[cols['password_status']],
                                        'account_status': account[cols['account_status']],
                                                                                 }
                except KeyError as e:
                    print("Error, KeyError: {}".format(str(e)))
                    break

                try:
                    account_name = account[cols['username']]
                    obj, created = Account.objects.update_or_create(username=account_name, defaults=account_values)
                    if created:
                        print("Success, account created:{}".format(account_name))
                    else:
                        print("Success, account updated:{}".format(account_name))
                    account_models.append(obj)
                except Exception as e:
                    print("Error, creating or updating account {}:{}".format(account_name, str(e)))
                    pass

    return account_models


def get_datetime_from_string(date_string, format):
    return make_aware(datetime.strptime(date_string, format))