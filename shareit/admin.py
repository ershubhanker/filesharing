from django.contrib import admin
#from share.forms import UploadedFile
from shareit.models import File

# Register your models here.

class FileAdmin(admin.ModelAdmin):
    fields = ["uploaded_at", "expires_at", "urlname", "duration", "Email"]
    list_display = ["uploaded_at", "duration",  "expires_at", "urlname", "file_link", "Email"]

admin.site.register(File, FileAdmin)