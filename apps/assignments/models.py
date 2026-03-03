from django.db import models
from django.utils import timezone


def assignment_attachment_path(instance, filename):
    return f'assignments/{instance.id or "new"}/{filename}'


def submission_file_path(instance, filename):
    return f'submissions/{instance.assignment_id}/{instance.student_id}/{filename}'


class Assignment(models.Model):
    SUBMISSION_TYPE_CHOICES = [
        ('file', 'File Upload'),
        ('text', 'Text Entry'),
        ('both', 'Both'),
    ]
    STATE_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey(
        'core.Subject', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assignments'
    )
    # Target class — either a form (whole year group) or a specific division
    form = models.ForeignKey(
        'core.SchoolForm', on_delete=models.CASCADE,
        related_name='assignments'
    )
    division = models.ForeignKey(
        'core.SchoolDivision', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assignments',
        help_text='Leave blank to assign to all divisions of the form'
    )
    academic_year = models.ForeignKey(
        'core.AcademicYear', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assignments'
    )
    teacher = models.ForeignKey(
        'faculty.FacultyInfo', on_delete=models.CASCADE,
        related_name='created_assignments'
    )
    due_date = models.DateTimeField()
    total_marks = models.PositiveIntegerField(null=True, blank=True)
    attachment = models.FileField(
        upload_to=assignment_attachment_path, null=True, blank=True,
        help_text='Assignment question paper / instruction file'
    )
    submission_type = models.CharField(
        max_length=10, choices=SUBMISSION_TYPE_CHOICES, default='file'
    )
    allow_late_submission = models.BooleanField(default=False)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='published')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.form}'

    @property
    def is_overdue(self):
        return timezone.now() > self.due_date

    @property
    def days_remaining(self):
        delta = self.due_date - timezone.now()
        return delta.days if delta.days >= 0 else 0

    @property
    def submission_count(self):
        return self.submissions.count()

    @property
    def graded_count(self):
        return self.submissions.filter(status='graded').count()


class AssignmentSubmission(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('late', 'Late'),
        ('graded', 'Graded'),
        ('returned', 'Returned'),
    ]

    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE,
        related_name='submissions'
    )
    student = models.ForeignKey(
        'students.StudentInfo', on_delete=models.CASCADE,
        related_name='assignment_submissions'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Submission content
    submission_file = models.FileField(
        upload_to=submission_file_path, null=True, blank=True
    )
    submission_text = models.TextField(blank=True)

    # Grading
    obtained_marks = models.PositiveIntegerField(null=True, blank=True)
    teacher_comment = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='submitted')
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        'faculty.FacultyInfo', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='graded_submissions'
    )

    class Meta:
        ordering = ['-submitted_at']
        unique_together = [['assignment', 'student']]

    def __str__(self):
        return f'{self.student} → {self.assignment.title}'

    @property
    def is_late(self):
        return self.submitted_at > self.assignment.due_date

    def save(self, *args, **kwargs):
        # Auto-set late status
        if self.submitted_at and self.assignment_id:
            try:
                if self.submitted_at > self.assignment.due_date and self.status == 'submitted':
                    self.status = 'late'
            except Exception:
                pass
        super().save(*args, **kwargs)
