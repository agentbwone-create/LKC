from rest_framework import serializers
from .models import AcademicYear, SchoolForm, SchoolDivision, Department, Subject, SubjectAllocation, Timetable


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'


class SchoolDivisionSerializer(serializers.ModelSerializer):
    form_name = serializers.CharField(source='form.name', read_only=True)
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = SchoolDivision
        fields = '__all__'

    def get_display_name(self, obj):
        return str(obj)


class SchoolFormSerializer(serializers.ModelSerializer):
    divisions = SchoolDivisionSerializer(many=True, read_only=True)
    student_count = serializers.IntegerField(read_only=True)
    division_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = SchoolForm
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    head_name = serializers.CharField(source='head.teacher_name', read_only=True)

    class Meta:
        model = Department
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Subject
        fields = '__all__'


class SubjectAllocationSerializer(serializers.ModelSerializer):
    form_name = serializers.CharField(source='form.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    division_name = serializers.SerializerMethodField()

    class Meta:
        model = SubjectAllocation
        fields = '__all__'

    def get_division_name(self, obj):
        return str(obj.division) if obj.division else ''


class TimetableSerializer(serializers.ModelSerializer):
    form_name = serializers.CharField(source='form.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    day_display = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = Timetable
        fields = '__all__'
