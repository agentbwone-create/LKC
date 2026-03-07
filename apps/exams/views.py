from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Exam, ExamResult
from .serializers import ExamSerializer, ExamResultSerializer


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.select_related('form', 'academic_year').all()
    serializer_class = ExamSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['exam_name', 'exam_code']

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get('state'):
            qs = qs.filter(state=params['state'])
        if params.get('form'):
            qs = qs.filter(form_id=params['form'])
        if params.get('division'):
            qs = qs.filter(division_id=params['division'])
        if params.get('academic_year'):
            qs = qs.filter(academic_year_id=params['academic_year'])
        return qs

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        exam = self.get_object()
        exam.state = 'confirmed'
        exam.save()
        return Response({'status': 'confirmed'})

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        exam = self.get_object()
        exam.state = 'ongoing'
        exam.save()
        return Response({'status': 'ongoing'})

    @action(detail=True, methods=['post'])
    def done(self, request, pk=None):
        exam = self.get_object()
        exam.state = 'done'
        exam.save()
        return Response({'status': 'done'})

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        exam = self.get_object()
        exam.state = 'cancelled'
        exam.save()
        return Response({'status': 'cancelled'})

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        exam = self.get_object()
        results = ExamResult.objects.filter(exam=exam).select_related(
            'student', 'subject', 'teacher', 'division'
        )
        return Response(ExamResultSerializer(results, many=True).data)


class ExamResultViewSet(viewsets.ModelViewSet):
    queryset = ExamResult.objects.select_related(
        'exam', 'student', 'subject', 'teacher', 'division'
    ).all()
    serializer_class = ExamResultSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__student_full_name', 'subject__name']

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get('exam'):
            qs = qs.filter(exam_id=params['exam'])
        if params.get('student'):
            qs = qs.filter(student_id=params['student'])
        if params.get('subject'):
            qs = qs.filter(subject_id=params['subject'])
        if params.get('state'):
            qs = qs.filter(state=params['state'])
        if params.get('teacher'):
            qs = qs.filter(teacher_id=params['teacher'])
        return qs

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        result = self.get_object()
        result.state = 'confirmed'
        result.save()
        return Response(ExamResultSerializer(result).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        result = self.get_object()
        result.state = 'teacher_approved'
        result.save()
        return Response(ExamResultSerializer(result).data)

    @action(detail=True, methods=['post'])
    def mark_done(self, request, pk=None):
        result = self.get_object()
        result.state = 'done'
        result.save()
        return Response(ExamResultSerializer(result).data)
