# from __future__ import unicode_literals

import io
from django.utils import timezone
import datetime

from django.db import models

from datetime import timedelta
from docx2pdf import convert


# Create your models here.


class File(models.Model):
    id = models.AutoField(primary_key=True)
    # name = models.CharField(max_length=500)

    uploaded_at = models.DateTimeField(default=timezone.now)

    duration = models.DurationField(default=timedelta())

    expires_at = models.DateTimeField(default=timezone.now() + timedelta(minutes=5))

    urlname = models.CharField(max_length=50, unique=True)
    file = models.FileField(upload_to='files')
    Email = models.CharField(max_length=30)

    def file_link(self):
        if self.file:
            # return "<a href='%s'> Download </a>" % (self.file.url)
            return self.file.url
        else: 
            return "No attatchement"

    file_link.allow_tags = True


class pdf_file(models.Model):
        file = models.FileField(upload_to='pdf_file')

class  docx_file(models.Model):
        file =models.FileField(upload_to='docx_file')

# class ConvertedFile(models.Model):
#     word_file = models.FileField(upload_to='word_files/')
#     pdf_file = models.FileField(upload_to='pdf_files/')

#     def __str__(self):
#         return f'{self.word_file.name} -> {self.pdf_file.name}'
    


class Document(models.Model):
    word_file = models.FileField(upload_to='word_files/')
    pdf_file = models.FileField(upload_to='pdf_files/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Convert Word file to PDF and save it to pdf_file field
        if not self.pk:  # Object is being created
            pdf_file = io.BytesIO()
            convert(self.word_file.file, pdf_file)
            self.pdf_file.save(self.word_file.name.replace('.docx', '.pdf'), pdf_file, save=False)

        super().save(*args, **kwargs)


class PDF(models.Model):
     name = models.CharField(max_length=255)
     file = models.FileField(upload_to='pdfs/')