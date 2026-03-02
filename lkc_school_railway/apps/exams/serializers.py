from rest_framework import serializers
from .models import Exam, ExamResult


class ExamSerializer(serializers.ModelSerializer):
    form_name = serializers.CharField(source='form.name', read_only=True)
    academic_year_name = serializers.CharField(source='academic_year.name', read_only=True)
    result_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Exam
        fields = '__all__'


class ExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.student_full_name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    exam_name = serializers.CharField(source='exam.exam_name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    division_name = serializers.SerializerMethodField()
    form_name = serializers.SerializerMethodField()

    class Meta:
        model = ExamResult
        fields = '__all__'

    def get_division_name(self, obj):
        return str(obj.division) if obj.division else ''

    def get_form_name(self, obj):
        return obj.exam.form.name if obj.exam else ''
