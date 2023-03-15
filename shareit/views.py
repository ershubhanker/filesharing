from django.shortcuts import render, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.utils import timezone
from shareit.models import File
from shareit.forms import FileForm
from datetime import timedelta
import schedule
import time
import os
import random, string
import csv

def index(request):

    return render(request, 'index.html', {})


def upload_file(request):
    # Handle file upload'
    #import pdb;pdb.set_trace();
    newfile = File()
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            newfile = File(file=request.FILES['file'])
            newfile.name = request.FILES['file'].name
            newfile.urlname = generate_string()
            # print(newfile.name)
            # print(newfile.urlname)
            print('hello', newfile.file_link)
            # file2= os.path.splitext(newfile.name)
            # print(file2)
            dur = request.POST['duration']
            d = get_duration(dur) # returns the correct duration as a timedelta
            # print(d)
            newfile.duration = d
            newfile.expires_at = newfile.uploaded_at + d

            newfile.save()

            # Redirect to the file list after POST
            # return HttpResponseRedirect(reverse('upload'))
    else:
        form = FileForm()  # A empty, unbound form

    return render(request,
        'yourfile.html',
        {'file': newfile, 'form': form, 'download_url': newfile.file_link}        
    )

def get_duration(dur):
    durations = {
        '5m' : timedelta(minutes=5),
        '1h' : timedelta(hours=1),
        '6h' : timedelta(hours=6),
        '24h' : timedelta(days=1),
        '3d' : timedelta(days=3)
    }

    for d in durations: 
        if d == dur:
            return durations[d]
    return timedelta()

def generate_string():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
 
def serve_download_page(request, urltext):

    file_to_download = File.objects.get(urlname=urltext)

    if file_to_download != None:
        return render(request,'yourfile.html', {'download' : file_to_download}, context_instance=RequestContext(request))
    else:
        return HttpResponseNotFound('Nothing here soz')
     

def email_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Emacil.csv"'
    fields = ['email Id']

    writer = csv.writer(response)
    
    # writer.writerow(['Email'])

    for Email in File.objects.all().values_list('Email'):
        writer.writerow(fields)
        writer.writerow(Email)
    

    return response
# def deletefiles(request):
#      print("Hello world")
#      delt = File.objects.all()
#      delt.delete()
#      return render(request,'delete.html')