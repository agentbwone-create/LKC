from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import StudentInfo
from .serializers import StudentSerializer, StudentListSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = StudentInfo.objects.select_related('form', 'division', 'parent').all()
    serializer_class = StudentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student_full_name', 'enrollment_number', 'email', 'mobile']
    ordering_fields = ['student_full_name', 'enrollment_number', 'form__sequence']

    def get_serializer_class(self):
        if self.action == 'list':
            return StudentListSerializer
        return StudentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get('form'):
            qs = qs.filter(form_id=params['form'])
        if params.get('division'):
            qs = qs.filter(division_id=params['division'])
        if params.get('state'):
            qs = qs.filter(state=params['state'])
        if params.get('academic_year'):
            qs = qs.filter(academic_year_id=params['academic_year'])
        return qs

    @action(detail=True, methods=['get'])
    def exam_results(self, request, pk=None):
        from apps.exams.models import ExamResult
        from apps.exams.serializers import ExamResultSerializer
        student = self.get_object()
        results = ExamResult.objects.filter(student=student).select_related(
            'exam', 'subject', 'teacher'
        )
        return Response(ExamResultSerializer(results, many=True).data)

    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        from apps.attendance.models import Attendance
        from apps.attendance.serializers import AttendanceSerializer
        student = self.get_object()
        records = Attendance.objects.filter(student=student).order_by('-date')[:30]
        return Response(AttendanceSerializer(records, many=True).data)
