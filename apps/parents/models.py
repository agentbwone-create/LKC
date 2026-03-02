from django.db import models

class SchoolParent(models.Model):
    RELATION_CHOICES = [
        ('father','Father'),('mother','Mother'),('guardian','Guardian'),
        ('grandparent','Grandparent'),('other','Other'),
    ]
    parent_name = models.CharField(max_length=200)
    is_parent = models.BooleanField(default=True)
    relation_with_child = models.CharField(max_length=20, choices=RELATION_CHOICES, default='father')
    photo = models.ImageField(upload_to='parents/', null=True, blank=True)
    street = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Botswana')
    phone = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    language_known = models.CharField(max_length=200, blank=True)
    occupation = models.CharField(max_length=100, blank=True)
    employer = models.CharField(max_length=200, blank=True)
    work_phone = models.CharField(max_length=30, blank=True)
    user = models.OneToOneField('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['parent_name']
        verbose_name = 'Parent'

    def __str__(self):
        return self.parent_name

    @property
    def student_count(self):
        return self.students.count()
