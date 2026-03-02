from rest_framework import viewsets, filters
from .models import SchoolParent
from .serializers import ParentSerializer

class ParentViewSet(viewsets.ModelViewSet):
    queryset = SchoolParent.objects.all()
    serializer_class = ParentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['parent_name', 'email', 'phone']
