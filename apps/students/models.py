from django.db import models
from datetime import date


class StudentInfo(models.Model):
    STATE_CHOICES = [
        ('active', 'Active'), ('graduated', 'Graduated'),
        ('transferred', 'Transferred'), ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ]
    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]
    BLOOD_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    student_full_name = models.CharField(max_length=200)
    enrollment_number = models.CharField(max_length=50, unique=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    birth_place = models.CharField(max_length=100, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_CHOICES, blank=True)
    photo = models.ImageField(upload_to='students/', null=True, blank=True)
    school_name = models.CharField(max_length=100, default='LKC')
    enrollment_date = models.DateField(null=True, blank=True)
    academic_year = models.ForeignKey(
        'core.AcademicYear', on_delete=models.SET_NULL, null=True, blank=True
    )
    form = models.ForeignKey(
        'core.SchoolForm', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='students'
    )
    division = models.ForeignKey(
        'core.SchoolDivision', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='students'
    )
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='active')
    street = models.CharField(max_length=200, blank=True)
    street2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Botswana')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=30, blank=True)
    parent = models.ForeignKey(
        'parents.SchoolParent', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='students'
    )
    guardian_name = models.CharField(max_length=200, blank=True)
    guardian_relation = models.CharField(max_length=100, blank=True)
    guardian_occupation = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=30, blank=True)
    guardian_email = models.EmailField(blank=True)
    guardian2_name = models.CharField(max_length=200, blank=True)
    guardian2_relation = models.CharField(max_length=100, blank=True)
    guardian2_occupation = models.CharField(max_length=100, blank=True)
    guardian2_phone = models.CharField(max_length=30, blank=True)
    guardian2_email = models.EmailField(blank=True)
    subjects = models.ManyToManyField('core.Subject', blank=True, related_name='students')
    is_achievement = models.BooleanField(default=False)
    award_name = models.CharField(max_length=200, blank=True)
    award_description = models.TextField(blank=True)
    medical_notes = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['enrollment_number']
        verbose_name = 'Student'

    def __str__(self):
        return self.student_full_name

    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            born = self.date_of_birth
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        return None
