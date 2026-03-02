from django.db import migrations, models
import django.db.models.deletion
import apps.assignments.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('faculty', '0001_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('due_date', models.DateTimeField()),
                ('total_marks', models.PositiveIntegerField(blank=True, null=True)),
                ('attachment', models.FileField(
                    blank=True, null=True,
                    help_text='Assignment question paper / instruction file',
                    upload_to=apps.assignments.models.assignment_attachment_path
                )),
                ('submission_type', models.CharField(
                    choices=[('file', 'File Upload'), ('text', 'Text Entry'), ('both', 'Both')],
                    default='file', max_length=10
                )),
                ('allow_late_submission', models.BooleanField(default=False)),
                ('state', models.CharField(
                    choices=[('draft', 'Draft'), ('published', 'Published'), ('closed', 'Closed')],
                    default='published', max_length=10
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('subject', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='assignments', to='core.subject'
                )),
                ('form', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='assignments', to='core.schoolform'
                )),
                ('division', models.ForeignKey(
                    blank=True, null=True,
                    help_text='Leave blank to assign to all divisions of the form',
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='assignments', to='core.schooldivision'
                )),
                ('academic_year', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='assignments', to='core.academicyear'
                )),
                ('teacher', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='created_assignments', to='faculty.facultyinfo'
                )),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='AssignmentSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('submitted_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('submission_file', models.FileField(
                    blank=True, null=True,
                    upload_to=apps.assignments.models.submission_file_path
                )),
                ('submission_text', models.TextField(blank=True)),
                ('obtained_marks', models.PositiveIntegerField(blank=True, null=True)),
                ('teacher_comment', models.TextField(blank=True)),
                ('status', models.CharField(
                    choices=[
                        ('submitted', 'Submitted'), ('late', 'Late'),
                        ('graded', 'Graded'), ('returned', 'Returned')
                    ],
                    default='submitted', max_length=10
                )),
                ('graded_at', models.DateTimeField(blank=True, null=True)),
                ('assignment', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='submissions', to='assignments.assignment'
                )),
                ('student', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='assignment_submissions', to='students.studentinfo'
                )),
                ('graded_by', models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='graded_submissions', to='faculty.facultyinfo'
                )),
            ],
            options={'ordering': ['-submitted_at']},
        ),
        migrations.AddConstraint(
            model_name='assignmentsubmission',
            constraint=models.UniqueConstraint(
                fields=['assignment', 'student'],
                name='unique_assignment_student'
            ),
        ),
    ]
