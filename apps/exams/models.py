from django.db import models
from django.core.exceptions import ValidationError


class Exam(models.Model):
    STATE_CHOICES = [
        ('draft', 'Draft'), ('confirmed', 'Confirmed'),
        ('ongoing', 'Ongoing'), ('done', 'Done'), ('cancelled', 'Cancelled'),
    ]
    exam_code = models.CharField(max_length=50, unique=True)
    exam_name = models.CharField(max_length=200)
    form = models.ForeignKey('core.SchoolForm', on_delete=models.CASCADE)
    division = models.ForeignKey(
        'core.SchoolDivision', on_delete=models.SET_NULL, null=True, blank=True
    )
    academic_year = models.ForeignKey(
        'core.AcademicYear', on_delete=models.CASCADE
    )
    exam_start_date = models.DateField(null=True, blank=True)
    exam_end_date = models.DateField(null=True, blank=True)
    subjects = models.ManyToManyField('core.Subject', blank=True)
    description = models.TextField(blank=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='draft')

    class Meta:
        ordering = ['-exam_start_date']

    def __str__(self):
        return self.exam_name

    @property
    def result_count(self):
        return self.results.count()


def compute_grade(percentage):
    if percentage >= 90: return 'A*'
    if percentage >= 80: return 'A'
    if percentage >= 70: return 'B'
    if percentage >= 60: return 'C'
    if percentage >= 50: return 'D'
    if percentage >= 40: return 'E'
    return 'U'


class ExamResult(models.Model):
    STATE_CHOICES = [
        ('draft', 'Draft'), ('confirmed', 'Confirmed'),
        ('teacher_approved', 'Teacher Approved'),
        ('done', 'Done'), ('re_evaluation', 'Re-Evaluation'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey('core.Subject', on_delete=models.CASCADE)
    student = models.ForeignKey('students.StudentInfo', on_delete=models.CASCADE, related_name='exam_results')
    division = models.ForeignKey(
        'core.SchoolDivision', on_delete=models.SET_NULL, null=True, blank=True
    )
    teacher = models.ForeignKey(
        'faculty.FacultyInfo', on_delete=models.SET_NULL, null=True, blank=True
    )
    obtain_marks = models.FloatField(default=0.0)
    minimum_marks = models.FloatField(default=40.0)
    maximum_marks = models.FloatField(default=100.0)
    percentage = models.FloatField(default=0.0)
    grade = models.CharField(max_length=5, blank=True)
    result = models.CharField(max_length=10, choices=[('pass', 'Pass'), ('fail', 'Fail')], blank=True)
    teacher_comment = models.TextField(blank=True)
    re_evaluation_marks = models.FloatField(default=0.0)
    re_evaluation_reason = models.TextField(blank=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='draft')

    class Meta:
        ordering = ['exam', 'student']

    def __str__(self):
        return f'{self.exam} / {self.student} / {self.subject}'

    def clean(self):
        if self.obtain_marks < 0:
            raise ValidationError('Obtained marks cannot be negative.')
        if self.maximum_marks > 0 and self.obtain_marks > self.maximum_marks:
            raise ValidationError('Obtained marks cannot exceed maximum marks.')

    def save(self, *args, **kwargs):
        if self.maximum_marks > 0:
            self.percentage = round((self.obtain_marks / self.maximum_marks) * 100, 2)
        else:
            self.percentage = 0.0
        self.grade = compute_grade(self.percentage)
        self.result = 'pass' if self.obtain_marks >= self.minimum_marks else 'fail'
        super().save(*args, **kwargs)
