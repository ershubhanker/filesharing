from configparser import ConverterMapping
import tempfile
from django.core.files.base import ContentFile
from lib2to3.pytree import convert
from apscheduler.schedulers.background import BackgroundScheduler
import fitz
from datetime import datetime, timedelta
import io
from fpdf import FPDF
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from shareit.models import pdf_file
from shareit.models import  Document
from shareit.models import  docx_file
from docx2pdf import convert
from pdf2image import convert_from_path
# from .models import ConvertedFile
import PyPDF2
from django.shortcuts import get_object_or_404, render, redirect
from apscheduler.schedulers.background import BackgroundScheduler
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseRedirect, HttpResponseServerError
from django.urls import reverse
from django.utils import timezone
# from filesharing.shareit.models import File
from shareit.models import File

from shareit.forms import FileForm, PDFUploadForm
from datetime import timedelta
from shareit.delete_expired_files import delete_expired_files
from django.http import FileResponse
import os
import random, string
import csv
from docx import Document
# from .models import PDFFile, WordFile

def index(request):
    # Schedule the deletion of expired files to occur every hou

    return render(request, 'index.html', {})

scheduler = BackgroundScheduler()
scheduler.start()

def delete_file(file_id):
    # Delete the file with the given file_id
    try:
        file_obj = File.objects.get(id=file_id)
        file_obj.delete()
        print(f"Deleted file with id {file_id}")
    except File.DoesNotExist:
        print(f"File with id {file_id} does not exist")

def schedule_file_deletion(file_id, duration):
    # Schedule the deletion of the file after the specified duration
    duration = get_duration(duration)
    if duration is not None:
        deletion_time = datetime.now() + duration
        scheduler.add_job(delete_file, 'date', run_date=deletion_time, args=[file_id])
        print(f"Scheduled deletion of file with id {file_id} at {deletion_time}")
def upload_file(request):
     # Handle file upload
    #import pdb; pdb.set_trace()
    newfile = File()
    if request.method == 'POST':
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            newfile = File(file=request.FILES['file'])
            newfile.name = request.FILES['file'].name
            newfile.urlname = generate_string()
            #print(newfile.file_link)
            newfile.save()
            print(newfile)
            dur = request.POST['duration']
            
            schedule_file_deletion(newfile.id, dur)
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

    return durations.get(dur, None)


def generate_string():
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(10))
 

     

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




    


def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run the delete_expired_files function every hour
    scheduler.add_job(delete_expired_files, 'interval', minutes=5)
    scheduler.start()

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
        pdf_file = io.BytesIO()
        convert(word_file.file, pdf_file)
         # Open the Word file using the python-docx library
      
        # Write the contents of the Word file to a PDF using the reportlab library
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(pdf_file.getbuffer())
            temp_pdf_file = f.name
            print(temp_pdf_file)
        
        # Send the PDF file as a response
        with open(temp_pdf_file, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="converted_file.pdf"'
            return response
    else:
        return render(request, 'converttopdf.html')
    

def pdf_upload(request):
    if request.method == 'POST':
        pdf_file = request.FILES.get('pdf')
        if not pdf_file:
            return render(request, 'pdf_upload.html', {'error': 'Please select a PDF file'})
        
        # Save the uploaded PDF file to the media directory
        with open(os.path.join(settings.PDF_MEDIA_ROOT, pdf_file.name), 'wb+') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)
        
        # Convert PDF to image
        with tempfile.TemporaryDirectory() as temp_dir:
            doc = fitz.open(os.path.join(settings.PDF_MEDIA_ROOT, pdf_file.name))
            page = doc[0] # Convert only the first page to image
            image_data = page.getPixmap(alpha=False).getPNGData()
        
        # Create a ContentFile object from the converted image data
        image_file = ContentFile(image_data)
        image_file.name = pdf_file.name.replace('.pdf', '.jpg')
        
        # Save the converted image file to the media directory
        with open(os.path.join(settings.PDF_MEDIA_ROOT, image_file.name), 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        # Generate a download response for the converted image file
        with open(os.path.join(settings.PDF_MEDIA_ROOT, image_file.name), 'rb') as file:
            response = HttpResponse(file.read(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="{image_file.name}"'
            return response
    
    return render(request, 'pdf_upload.html')