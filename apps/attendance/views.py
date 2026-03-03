from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from .models import Attendance, AttendanceRegister
from .serializers import AttendanceSerializer, AttendanceRegisterSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('student', 'teacher').all()
    serializer_class = AttendanceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['student__student_full_name']

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        if p.get('date'): qs = qs.filter(date=p['date'])
        if p.get('student'): qs = qs.filter(student_id=p['student'])
        if p.get('state'): qs = qs.filter(state=p['state'])
        if p.get('form'): qs = qs.filter(student__form_id=p['form'])
        if p.get('division'): qs = qs.filter(student__division_id=p['division'])
        return qs

    @action(detail=False, methods=['get'])
    def summary(self, request):
        from django.utils import timezone
        date = request.query_params.get('date', timezone.now().date())
        summary = Attendance.objects.filter(date=date).values('state').annotate(count=Count('id'))
        return Response({item['state']: item['count'] for item in summary})

class AttendanceRegisterViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRegister.objects.select_related('form', 'division', 'teacher').all()
    serializer_class = AttendanceRegisterSerializer
