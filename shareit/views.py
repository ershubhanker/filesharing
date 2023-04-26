from configparser import ConverterMapping
import datetime
from lib2to3.pytree import convert
from win32com import client
import re
import io
import traceback
from xmlrpc.server import DocXMLRPCRequestHandler
import comtypes.client
import docx
from fpdf import FPDF
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from shareit.models import pdf_file
from shareit.models import  docx_file
import PyPDF2
from django.shortcuts import get_object_or_404, render, redirect
from apscheduler.schedulers.background import BackgroundScheduler
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect, HttpResponseServerError
from django.urls import reverse
from django.utils import timezone
# from filesharing.shareit.models import File
from shareit.models import File
from shareit.forms import FileForm

from datetime import timedelta
from shareit.delete_expired_files import delete_expired_files
import schedule
import mimetypes
from django.http import FileResponse
import time
import os
import random, string
import csv
from docx import Document
# from .models import PDFFile, WordFile

def index(request):
    # Schedule the deletion of expired files to occur every hour
    start_scheduler()
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_expired_files, 'interval', minutes=5)

    return render(request, 'index.html', {})
# cwd = os.getcwd()

# # Print the current working directory to the console for debugging purposes
# print(cwd)

# # Change the current working directory to the MEDIA_ROOT
# os.chdir(settings.MEDIA_ROOT)

# # Print the current working directory to the console for debugging purposes
# print(os.getcwd())

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
            #newfile=FileForm.objects.create(newfile=newfile)
            newfile.save()

            # Redirect to the file list after POST
            # return HttpResponseRedirect(reverse('upload'))
    else:
        form = FileForm()  # A empty, unbound form

    return render(request,
        'yourfile.html',
        {'file': newfile, 'form': form, 'download_url': newfile.file_link}        
    )

    # form = FileForm()  # create an empty form
    # return render(request, 'yourfile.html', {'file': new_file, 'form': form})

def get_duration(duration):
    durations = {
        '5m' : timedelta(minutes=5),
        '1h' : timedelta(hours=1),
        '6h' : timedelta(hours=6),
        '24h' : timedelta(days=1),
        '3d' : timedelta(days=3)
    }

    if duration in durations:
        return durations[duration]
    else:
        # Return a default duration of 5 minutes
        return timedelta(minutes=5)


def generate_string():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
 
# def serve_download_page(request, urltext):

#     file_to_download = File.objects.get(urlname=urltext)

#     if file_to_download != None:
#         return render(request,'yourfile.html', {'download' : file_to_download}, context_instance=RequestContext(request))
#     else:
#         return HttpResponseNotFound('Nothing here soz')
     

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



    
def delete_expired_files():
    import pdb;pdb.set_trace()
    print("Deleting expired files...")
    expired_files = File.objects.filter(expires_at__lte=timezone.now())
    for file_path in expired_files:
        print(f"Deleting expired file: {file_path}")
        os.remove(file_path)
    


def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run the delete_expired_files function every hour
    scheduler.add_job(delete_expired_files, 'interval', minutes=5)
    scheduler.start()
# def deletefiles(request):
#      print("Hello world")
#      delt = File.objects.all()
#      delt.delete()
#      return render(request,'delete.html')

# def download_file(request, urltext):
#     # Retrieve the File object corresponding to the given URL name
#     file_to_download = get_object_or_404(File, urlname=urltext)

#     # Check if the file has expired (based on its expiration time)
#     if file_to_download.expires_at < timezone.now():
#         # Return an HTTP response indicating that the file has expired
#         return HttpResponse('This file has expired.')

#     # Open the file and read its contents into a byte string
#     with open(file_to_download.file.path, 'rb') as f:
#         file_contents = f.read()
#         response = HttpResponse(file_contents, content_type=file_to_download.content_type)
#     response['Content-Disposition'] = f'attachment; filename="{file_to_download.name}"'
#     response['Content-Length'] = len(file_contents)

    # Return the response object
    # return response


# def download_file(request, urltext):
#     file_to_download = File.objects.get(urlname=urltext)

#     if file_to_download is not None:
#         file_path = file_to_download.file.path
#         with open(file_path, 'rb') as f:
#             content_type = mimetypes.guess_type(file_path)[0]
#             response = FileResponse(f, content_type=content_type)
#             response['Content-Disposition'] = f'attachment; filename="{file_to_download.file.name}"'
#             return response
#     else:
#         return HttpResponseNotFound('Nothing here soz')
def download_file(request, urlname):
    # Retrieve the File object corresponding to the given URL name
    file_to_download = get_object_or_404(File, urlname=urlname)

    # Check if the file has expired (based on its expiration time)
    if file_to_download.expires_at < timezone.now():
        # Return an HTTP response indicating that the file has expired
        return HttpResponse('This file has expired.')

    # Get the full path to the file on the server's filesystem
    file_path = f"{settings.MEDIA_ROOT}/{file_to_download.file.name}"

    # Open the file and read its contents into a byte string
    with open(file_path, 'rb') as f:
        file_data = f.read()

    # Create a Django FileResponse object to stream the file to the client
    response = FileResponse(file_data)

    # Set the Content-Type header based on the file's MIME type
    content_type = file_to_download.file.content_type
    response['Content-Type'] = content_type

    # Set the Content-Disposition header to force a "Save As" dialog box
    response['Content-Disposition'] = f'attachment; filename="{file_to_download.name}"'

    # Return the FileResponse object
    return response
    

def convert_pdf_to_word(request):
    if request.method == 'POST':
        pdf_file = request.FILES['pdf_file']
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        word_doc = Document()
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            word_doc.add_paragraph(text)
        output = io.BytesIO()
        word_doc.save(output)
        response = HttpResponse(content_type='application/msword')
        response['Content-Disposition'] = 'attachment; filename="converted_file.docx"'
        response.write(output.getvalue())
        return response
    else:
        return render(request, 'converttoworf.html')
    

def convert_word_to_pdf(request):
    if request.method == 'POST':
        word_file = request.FILES['word_file']
        word_path = os.path.join('media', word_file.name)
        with open(word_path, 'wb') as f:
            f.write(word_file.read())
        word = client.DispatchEx("Word.Application")
        worddoc = word.Documents.Open(os.path.abspath(word_path))
        pdf_path = os.path.join('media', f'{os.path.splitext(word_file.name)[0]}.pdf')
        worddoc.SaveAs(pdf_path, FileFormat=17)
        worddoc.Close()
        word.Quit()
        with open(pdf_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
            return response
    return render(request, 'converttopdf.html')