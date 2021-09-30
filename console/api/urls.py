from django.urls import re_path, include
from api.views.IVAD import IVAD, DownloadCase
from api.views.reactStudy import ReactStudy

urlpatterns = [
    re_path(r'infoVerificationAndDownload/', IVAD.as_view(), name='IVAD'),
    re_path(r'download/(?P<uid>\w+)', DownloadCase.as_view(), name='donwload'),
    re_path(r'reactStudy/', ReactStudy.as_view(), name='rc'),
]