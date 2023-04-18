"""filesharing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static
from django.contrib import admin
from shareit import views


urlpatterns = [
    #path(r'^', include(shareurls)),
    path('', views.index, name="index"),
    path('upload/', views.upload_file, name="upload"),
    # path('download/(?P<urltext>\w+)', views.serve_download_page, name="download"),
    #path('delete/', views.deletefiles, name="delete"),
    path('admin_master/', admin.site.urls),
    path('email_csv', views.email_csv, name="email_csv"),
    path('convert/', views.convert_pdf_to_word, name='convert_pdf_to_word'),
    path('convertpdf/', views.convert_word_to_pdf, name='convert_word_to_pdf'),
]

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
