from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParentViewSet
router = DefaultRouter()
router.register('', ParentViewSet, basename='parents')
urlpatterns = [path('', include(router.urls))]
