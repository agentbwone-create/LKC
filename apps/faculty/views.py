from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import FacultyInfo
from .serializers import FacultySerializer, FacultyListSerializer


class FacultyViewSet(viewsets.ModelViewSet):
    queryset = FacultyInfo.objects.select_related('department').prefetch_related('subjects').all()
    serializer_class = FacultySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['teacher_name', 'teacher_code', 'work_email']
    ordering_fields = ['teacher_name', 'joining_date', 'state']

    def get_serializer_class(self):
        if self.action == 'list':
            return FacultyListSerializer
        return FacultySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        state = self.request.query_params.get('state')
        dept = self.request.query_params.get('department')
        if state:
            qs = qs.filter(state=state)
        if dept:
            qs = qs.filter(department_id=dept)
        return qs
