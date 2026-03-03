from rest_framework import serializers
from .models import SchoolParent

class ParentSerializer(serializers.ModelSerializer):
    student_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = SchoolParent
        fields = '__all__'
