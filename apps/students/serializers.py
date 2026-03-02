from rest_framework import serializers
from .models import StudentInfo


class StudentListSerializer(serializers.ModelSerializer):
    form_name = serializers.CharField(source='form.name', read_only=True)
    division_name = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.parent_name', read_only=True)

    class Meta:
        model = StudentInfo
        fields = ['id', 'student_full_name', 'enrollment_number', 'gender',
                  'form_name', 'division_name', 'state', 'parent_name', 'mobile']

    def get_division_name(self, obj):
        return str(obj.division) if obj.division else ''


class StudentSerializer(serializers.ModelSerializer):
    form_name = serializers.CharField(source='form.name', read_only=True)
    division_name = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.parent_name', read_only=True)
    age = serializers.IntegerField(read_only=True)
    subjects_list = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = StudentInfo
        fields = '__all__'

    def get_division_name(self, obj):
        return str(obj.division) if obj.division else ''

    def get_subjects_list(self, obj):
        return [{'id': s.id, 'name': s.name} for s in obj.subjects.all()]

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
        return None
