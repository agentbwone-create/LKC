from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExamViewSet, ExamResultViewSet
router = DefaultRouter()
router.register('results', ExamResultViewSet, basename='exam-results')
router.register('', ExamViewSet, basename='exams')
urlpatterns = [path('', include(router.urls))]
