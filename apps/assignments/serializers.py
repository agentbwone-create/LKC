from rest_framework import serializers
from django.utils import timezone
from .models import Assignment, AssignmentSubmission


class AssignmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    form_name = serializers.CharField(source='form.name', read_only=True)
    division_name = serializers.SerializerMethodField()
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    submission_count = serializers.IntegerField(read_only=True)
    graded_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'subject_name', 'form_name', 'division_name',
            'teacher_name', 'due_date', 'total_marks', 'submission_type',
            'allow_late_submission', 'state', 'is_overdue', 'days_remaining',
            'submission_count', 'graded_count', 'created_at',
        ]

    def get_division_name(self, obj):
        return str(obj.division) if obj.division else 'All Divisions'


class AssignmentSerializer(serializers.ModelSerializer):
    """Full serializer for create/detail views."""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    form_name = serializers.CharField(source='form.name', read_only=True)
    division_name = serializers.SerializerMethodField()
    teacher_name = serializers.CharField(source='teacher.teacher_name', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
    submission_count = serializers.IntegerField(read_only=True)
    graded_count = serializers.IntegerField(read_only=True)
    attachment_url = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['teacher', 'created_at', 'updated_at']

    def get_division_name(self, obj):
        return str(obj.division) if obj.division else 'All Divisions'

    def get_attachment_url(self, obj):
        if obj.attachment:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment.url)
        return None

    def validate_due_date(self, value):
        # Allow past due dates for edits; only warn on creation
        if self.instance is None and value < timezone.now():
            raise serializers.ValidationError('Due date cannot be in the past.')
        return value


class SubmissionSerializer(serializers.ModelSerializer):
    """For teachers viewing submissions."""
    student_name = serializers.CharField(source='student.student_full_name', read_only=True)
    student_enrollment = serializers.CharField(source='student.enrollment_number', read_only=True)
    student_division = serializers.SerializerMethodField()
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    is_late = serializers.BooleanField(read_only=True)
    submission_file_url = serializers.SerializerMethodField()
    graded_by_name = serializers.CharField(source='graded_by.teacher_name', read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = '__all__'
        read_only_fields = ['student', 'assignment', 'submitted_at', 'updated_at']

    def get_student_division(self, obj):
        if obj.student and obj.student.division:
            return str(obj.student.division)
        return ''

    def get_submission_file_url(self, obj):
        if obj.submission_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.submission_file.url)
        return None


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """For students creating their own submission."""
    class Meta:
        model = AssignmentSubmission
        fields = ['assignment', 'submission_file', 'submission_text']

    def validate(self, data):
        assignment = data.get('assignment')
        request = self.context.get('request')

        if not assignment:
            raise serializers.ValidationError('Assignment is required.')

        # Check due date
        if assignment.is_overdue and not assignment.allow_late_submission:
            raise serializers.ValidationError(
                'This assignment is past the due date and does not allow late submissions.'
            )

        # Validate submission type
        sub_type = assignment.submission_type
        if sub_type == 'file' and not data.get('submission_file'):
            raise serializers.ValidationError('A file submission is required for this assignment.')
        if sub_type == 'text' and not data.get('submission_text', '').strip():
            raise serializers.ValidationError('A text submission is required for this assignment.')

        return data


class GradeSubmissionSerializer(serializers.ModelSerializer):
    """For teachers grading a submission."""
    class Meta:
        model = AssignmentSubmission
        fields = ['obtained_marks', 'teacher_comment', 'status']

    def validate_obtained_marks(self, value):
        if value is not None and self.instance:
            total = self.instance.assignment.total_marks
            if total and value > total:
                raise serializers.ValidationError(
                    f'Obtained marks ({value}) cannot exceed total marks ({total}).'
                )
        return value
