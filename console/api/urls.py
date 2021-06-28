from django.urls import re_path, include
from api.views.IVAD import IVAD, DownloadCase

urlpatterns = [
    re_path(r'infoVerificationAndDownload/', IVAD.as_view(), name='IVAD'),
    re_path(r'download/(?P<uid>\w+)', DownloadCase.as_view(), name='donwload')
]