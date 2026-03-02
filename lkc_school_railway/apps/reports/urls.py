from django.urls import path
from .views import HODReportView, ReportPreviewView
urlpatterns = [
    path('hod-report/', HODReportView.as_view(), name='hod-report'),
    path('hod-preview/', ReportPreviewView.as_view(), name='hod-preview'),
]
