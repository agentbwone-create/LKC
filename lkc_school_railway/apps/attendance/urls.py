from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet, AttendanceRegisterViewSet
router = DefaultRouter()
router.register('registers', AttendanceRegisterViewSet, basename='registers')
router.register('', AttendanceViewSet, basename='attendance')
urlpatterns = [path('', include(router.urls))]
