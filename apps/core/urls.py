from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (AcademicYearViewSet, SchoolFormViewSet, SchoolDivisionViewSet,
                    DepartmentViewSet, SubjectViewSet, SubjectAllocationViewSet,
                    TimetableViewSet, DashboardView)

router = DefaultRouter()
router.register('academic-years', AcademicYearViewSet)
router.register('forms', SchoolFormViewSet)
router.register('divisions', SchoolDivisionViewSet)
router.register('departments', DepartmentViewSet)
router.register('subjects', SubjectViewSet)
router.register('subject-allocations', SubjectAllocationViewSet)
router.register('timetables', TimetableViewSet)
router.register('dashboard', DashboardView, basename='dashboard')

urlpatterns = [path('', include(router.urls))]
