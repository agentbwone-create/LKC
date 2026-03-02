from rest_framework import serializers
from .models import Attendance, AttendanceRegister

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.student_full_name', read_only=True)
    form_name = serializers.SerializerMethodField()
    division_name = serializers.SerializerMethodField()
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'

    def get_form_name(self, obj):
        return obj.student.form.name if obj.student.form else ''

    def get_division_name(self, obj):
        return str(obj.student.division) if obj.student.division else ''

class AttendanceRegisterSerializer(serializers.ModelSerializer):
    form_name = serializers.CharField(source='form.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    class Meta:
        model = AttendanceRegister
        fields = '__all__'
