from django.db import models


class Attendance(models.Model):
    STATE_CHOICES = [
        ('present', 'Present'), ('absent', 'Absent'),
        ('late', 'Late'), ('excused', 'Excused'),
    ]
    PERIOD_CHOICES = [
        ('morning', 'Morning'), ('afternoon', 'Afternoon'), ('full_day', 'Full Day'),
    ]

    student = models.ForeignKey(
        'students.StudentInfo', on_delete=models.CASCADE, related_name='attendance_records'
    )
    date = models.DateField()
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default='present')
    period = models.CharField(max_length=15, choices=PERIOD_CHOICES, default='full_day')
    academic_year = models.ForeignKey(
        'core.AcademicYear', on_delete=models.SET_NULL, null=True, blank=True
    )
    teacher = models.ForeignKey(
        'faculty.FacultyInfo', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='marked_attendance'
    )
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', 'student']
        unique_together = [['student', 'date', 'period']]

    def __str__(self):
        return f'{self.student} - {self.date} - {self.state}'


class AttendanceRegister(models.Model):
    name = models.CharField(max_length=200)
    form = models.ForeignKey('core.SchoolForm', on_delete=models.CASCADE)
    division = models.ForeignKey(
        'core.SchoolDivision', on_delete=models.SET_NULL, null=True, blank=True
    )
    date = models.DateField()
    academic_year = models.ForeignKey(
        'core.AcademicYear', on_delete=models.SET_NULL, null=True, blank=True
    )
    teacher = models.ForeignKey(
        'faculty.FacultyInfo', on_delete=models.SET_NULL, null=True, blank=True
    )
    state = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('confirmed', 'Confirmed')],
        default='draft'
    )

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.name
