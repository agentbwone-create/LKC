from django.db import models


class AcademicYear(models.Model):
    name = models.CharField(max_length=20, unique=True)
    date_start = models.DateField()
    date_end = models.DateField()
    is_current = models.BooleanField(default=False)
    state = models.CharField(max_length=10, choices=[
        ('draft', 'Draft'), ('active', 'Active'), ('closed', 'Closed')
    ], default='draft')
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class SchoolForm(models.Model):
    name = models.CharField(max_length=50, unique=True)
    sequence = models.IntegerField(default=10)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['sequence', 'name']

    def __str__(self):
        return self.name

    @property
    def student_count(self):
        return self.students.count()

    @property
    def division_count(self):
        return self.divisions.count()


class SchoolDivision(models.Model):
    name = models.CharField(max_length=30)
    form = models.ForeignKey(SchoolForm, on_delete=models.CASCADE, related_name='divisions')
    teacher = models.ForeignKey(
        'faculty.FacultyInfo', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='class_teacher_divisions'
    )

    class Meta:
        ordering = ['form', 'name']
        unique_together = [['name', 'form']]

    def __str__(self):
        return f'{self.form.name} {self.name}'


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    head = models.ForeignKey(
        'faculty.FacultyInfo', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='headed_departments'
    )
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='subjects'
    )
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SubjectAllocation(models.Model):
    form = models.ForeignKey(SchoolForm, on_delete=models.CASCADE)
    division = models.ForeignKey(SchoolDivision, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey('faculty.FacultyInfo', on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['form', 'subject']
        unique_together = [['form', 'division', 'subject', 'academic_year']]

    def __str__(self):
        return f'{self.form} / {self.subject} / {self.teacher}'


class Timetable(models.Model):
    DAY_CHOICES = [
        ('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
        ('3', 'Thursday'), ('4', 'Friday'),
    ]
    form = models.ForeignKey(SchoolForm, on_delete=models.CASCADE)
    division = models.ForeignKey(SchoolDivision, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        'faculty.FacultyInfo', on_delete=models.SET_NULL, null=True, blank=True
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True)
    day_of_week = models.CharField(max_length=1, choices=DAY_CHOICES)
    period_number = models.IntegerField()
    time_start = models.TimeField(null=True, blank=True)
    time_end = models.TimeField(null=True, blank=True)
    room = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['day_of_week', 'period_number']

    def __str__(self):
        return f'{self.form} - {self.subject} - {self.get_day_of_week_display()}'
