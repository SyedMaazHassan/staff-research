from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import time
from .models import *
from uuid import uuid4
import csv
from django.http import HttpResponse
from django.views import View
import csv
import zipfile
from io import BytesIO
from datetime import datetime
from django.contrib import messages


def single_report_view(request, request_id):
    try:
        scrap_request = ScrapRequest.objects.filter(request_id = request_id).first()
    except Exception as e:
        messages.error(request, str(e))
        return redirect('home')
    
    if not scrap_request:
        return redirect('home')

    context = {
        'scrap_request': scrap_request,
        'websites': Website.objects.filter(request = scrap_request, is_success=True),
        'websites2': Website.objects.filter(request = scrap_request, is_success=False),
    }
    return render(request, 'single-report.html', context)

class ExportCSVView(View):
    def get(self, request, request_id, *args, **kwargs):
        if not request_id:
            return redirect('home')
        try:
            scrap_request = ScrapRequest.objects.filter(request_id = request_id).first()
        except Exception as e:
            messages.error(request, str(e))
            return redirect('home')
        
        if not scrap_request:
            return redirect('home')

        # Retrieve data for Researched.csv
        researched_data = Website.objects.filter(request=scrap_request, is_success=True)
        
        # Retrieve data for FailedToResearched.csv
        failed_data = Website.objects.filter(request=scrap_request, is_success=False)

        # Create Researched.csv
        researched_csv_content = "Name,Job Title,Email,OrgID,URL\n"
        for website in researched_data:
            for staff_member in website.staffmember_set.all():
                researched_csv_content += f'{staff_member.name},{staff_member.job_title},{staff_member.email},{website.org_id},{website.url}\n'

        # Create FailedToResearched.csv
        failed_csv_content = "OrgID,URL\n"

        for website in failed_data:
            failed_csv_content += f'{website.org_id},{website.url}\n'

        # Generate the current date in the desired format (e.g., "2023-03-03")
        current_date = scrap_request.created_at.strftime("%Y-%m-%d")

        # Create a zip file containing both CSVs
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.writestr('Researched.csv', researched_csv_content)
            zip_file.writestr('FailedToResearched.csv', failed_csv_content)

        # Create a single response with the zip file
        response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="Staff-Research-Report-{current_date}.zip"'

        return response



def home_view(request):
    context = {
        'page': 'home',
        'request_id': str(uuid4())
    }
    return render(request, 'home.html', context)

def fetch_staff_view(request):
    url = request.GET.get('URL')
    org_id = request.GET.get('OrgID')
    request_id = request.GET.get('request_id')

    scrap_request, created = ScrapRequest.objects.get_or_create(
        request_id = request_id
    )

    website = Website.objects.create(
        url = url,
        org_id = str(org_id),
        request = scrap_request
    )
    website.scrap_staff()

    output = {
        'id': website.id,
        'status': website.is_success
    }

    time.sleep(1)
    return JsonResponse(output)

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')
