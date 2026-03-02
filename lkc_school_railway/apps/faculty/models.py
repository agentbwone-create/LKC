from django.db import models


class FacultyInfo(models.Model):
    STATE_CHOICES = [
        ('active', 'Active'), ('on_leave', 'On Leave'),
        ('resigned', 'Resigned'), ('retired', 'Retired'),
    ]
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]
    MARITAL_CHOICES = [
        ('single', 'Single'), ('married', 'Married'),
        ('divorced', 'Divorced'), ('widowed', 'Widowed'),
    ]

    teacher_name = models.CharField(max_length=200)
    teacher_code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    joining_date = models.DateField(null=True, blank=True)
    school_name = models.CharField(max_length=100, default='LKC')
    department = models.ForeignKey(
        'core.Department', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='teachers'
    )
    job_position = models.CharField(max_length=100, default='Teacher')
    photo = models.ImageField(upload_to='faculty/', null=True, blank=True)
    work_phone = models.CharField(max_length=30, blank=True)
    work_mobile = models.CharField(max_length=30, blank=True)
    work_email = models.EmailField(blank=True)
    work_location = models.CharField(max_length=100, blank=True)
    street = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Botswana')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    id_number = models.CharField(max_length=50, blank=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_CHOICES, blank=True)
    spouse_name = models.CharField(max_length=200, blank=True)
    language_known = models.CharField(max_length=200, blank=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    emergency_phone = models.CharField(max_length=30, blank=True)
    qualification = models.CharField(max_length=200, blank=True)
    experience_years = models.IntegerField(default=0)
    subjects = models.ManyToManyField('core.Subject', blank=True, related_name='teachers')
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='active')
    user = models.OneToOneField(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='faculty_profile'
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['teacher_name']
        verbose_name = 'Teacher'

    def __str__(self):
        return self.teacher_name
