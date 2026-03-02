from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AcademicYear, SchoolForm, SchoolDivision, Department, Subject, SubjectAllocation, Timetable
from .serializers import (AcademicYearSerializer, SchoolFormSerializer, SchoolDivisionSerializer,
                           DepartmentSerializer, SubjectSerializer, SubjectAllocationSerializer,
                           TimetableSerializer)


class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer

    @action(detail=False, methods=['get'])
    def current(self, request):
        year = AcademicYear.objects.filter(is_current=True).first()
        if year:
            return Response(AcademicYearSerializer(year).data)
        return Response({'detail': 'No current academic year set.'}, status=404)


class SchoolFormViewSet(viewsets.ModelViewSet):
    queryset = SchoolForm.objects.prefetch_related('divisions').all()
    serializer_class = SchoolFormSerializer


class SchoolDivisionViewSet(viewsets.ModelViewSet):
    queryset = SchoolDivision.objects.select_related('form').all()
    serializer_class = SchoolDivisionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        form_id = self.request.query_params.get('form')
        if form_id:
            qs = qs.filter(form_id=form_id)
        return qs


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.select_related('department').all()
    serializer_class = SubjectSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.query_params.get('active'):
            qs = qs.filter(is_active=True)
        return qs


class SubjectAllocationViewSet(viewsets.ModelViewSet):
    queryset = SubjectAllocation.objects.select_related('form', 'division', 'subject', 'teacher').all()
    serializer_class = SubjectAllocationSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        form_id = self.request.query_params.get('form')
        year_id = self.request.query_params.get('academic_year')
        if form_id:
            qs = qs.filter(form_id=form_id)
        if year_id:
            qs = qs.filter(academic_year_id=year_id)
        return qs


class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.select_related('form', 'division', 'subject', 'teacher').all()
    serializer_class = TimetableSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        form_id = self.request.query_params.get('form')
        division_id = self.request.query_params.get('division')
        if form_id:
            qs = qs.filter(form_id=form_id)
        if division_id:
            qs = qs.filter(division_id=division_id)
        return qs


class DashboardView(viewsets.ViewSet):
    def list(self, request):
        from apps.students.models import StudentInfo
        from apps.faculty.models import FacultyInfo
        from apps.parents.models import SchoolParent
        from apps.exams.models import Exam, ExamResult
        from apps.attendance.models import Attendance
        from django.utils import timezone

        today = timezone.now().date()

        stats = {
            'students': {
                'total': StudentInfo.objects.count(),
                'active': StudentInfo.objects.filter(state='active').count(),
                'by_form': list(
                    StudentInfo.objects.filter(state='active')
                    .values('form__name')
                    .annotate(count=__import__('django.db.models', fromlist=['Count']).Count('id'))
                    .order_by('form__sequence')
                ),
            },
            'teachers': {
                'total': FacultyInfo.objects.count(),
                'active': FacultyInfo.objects.filter(state='active').count(),
            },
            'parents': {
                'total': SchoolParent.objects.count(),
            },
            'exams': {
                'total': Exam.objects.count(),
                'draft': Exam.objects.filter(state='draft').count(),
                'confirmed': Exam.objects.filter(state='confirmed').count(),
                'ongoing': Exam.objects.filter(state='ongoing').count(),
                'done': Exam.objects.filter(state='done').count(),
            },
            'attendance_today': {
                'present': Attendance.objects.filter(date=today, state='present').count(),
                'absent': Attendance.objects.filter(date=today, state='absent').count(),
                'late': Attendance.objects.filter(date=today, state='late').count(),
                'excused': Attendance.objects.filter(date=today, state='excused').count(),
            },
            'current_year': None,
        }

        current_year = AcademicYear.objects.filter(is_current=True).first()
        if current_year:
            stats['current_year'] = AcademicYearSerializer(current_year).data

        return Response(stats)
