from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssignmentViewSet, SubmissionViewSet

router = DefaultRouter()
router.register('', AssignmentViewSet, basename='assignment')
router.register('submissions', SubmissionViewSet, basename='submission')

urlpatterns = [path('', include(router.urls))]
