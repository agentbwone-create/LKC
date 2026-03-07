from django.urls import path
from .views import HODReportView, ReportPreviewView, ClassTeacherPerformanceView
urlpatterns = [
    path('hod-report/', HODReportView.as_view(), name='hod-report'),
    path('hod-preview/', ReportPreviewView.as_view(), name='hod-preview'),
    path('class-performance/', ClassTeacherPerformanceView.as_view(), name='class-performance'),
]
