from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('apps.core.urls')),
    path('api/students/', include('apps.students.urls')),
    path('api/faculty/', include('apps.faculty.urls')),
    path('api/parents/', include('apps.parents.urls')),
    path('api/exams/', include('apps.exams.urls')),
    path('api/attendance/', include('apps.attendance.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/assignments/', include('apps.assignments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
