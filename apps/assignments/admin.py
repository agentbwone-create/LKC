from django.contrib import admin
from .models import Assignment, AssignmentSubmission


class SubmissionInline(admin.TabularInline):
    model = AssignmentSubmission
    extra = 0
    readonly_fields = ['submitted_at', 'updated_at', 'graded_at', 'is_late']
    fields = ['student', 'status', 'obtained_marks', 'teacher_comment', 'submitted_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'form', 'division', 'teacher', 'due_date', 'state',
                    'submission_count', 'graded_count']
    list_filter = ['state', 'form', 'submission_type', 'allow_late_submission']
    search_fields = ['title', 'description', 'teacher__teacher_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SubmissionInline]


@admin.register(AssignmentSubmission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'status', 'submitted_at', 'obtained_marks']
    list_filter = ['status', 'assignment__form']
    search_fields = ['student__student_full_name', 'assignment__title']
    readonly_fields = ['submitted_at', 'updated_at', 'graded_at']
