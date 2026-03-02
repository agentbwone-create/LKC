from rest_framework import serializers
from .models import FacultyInfo


class FacultySerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    subjects_list = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = FacultyInfo
        fields = '__all__'

    def get_subjects_list(self, obj):
        return [{'id': s.id, 'name': s.name} for s in obj.subjects.all()]

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
        return None


class FacultyListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = FacultyInfo
        fields = ['id', 'teacher_name', 'teacher_code', 'department_name',
                  'work_email', 'work_phone', 'state', 'job_position']
