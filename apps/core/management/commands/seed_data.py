from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import AcademicYear, SchoolForm, SchoolDivision, Department, Subject
from apps.faculty.models import FacultyInfo
from apps.students.models import StudentInfo
from apps.parents.models import SchoolParent
from apps.exams.models import Exam, ExamResult
from apps.attendance.models import Attendance
from datetime import date, timedelta
import random


TEACHER_DATA = [
    ('Ms. Makoni', 'T001', 'ICT', 'Teaching / IT'),
    ('Mr. Chivorese', 'T002', 'Sciences', 'Teaching / Sciences'),
    ('Ms. Madzivanyika', 'T003', 'Maths', 'Teaching / Maths'),
    ('Mr. Banda', 'T004', 'Languages', 'Teaching / Languages'),
    ('Ms. Sithole', 'T005', 'Business', 'Teaching / Business'),
    ('Mr. Dube', 'T006', 'Humanities', 'Teaching / Humanities'),
    ('Ms. Phiri', 'T007', 'Sciences', 'Teaching / Sciences'),
    ('Mr. Moyo', 'T008', 'Maths', 'Teaching / Maths'),
    ('Ms. Nkosi', 'T009', 'IT', 'Teaching / IT'),
    ('Mr. Tau', 'T010', 'Business', 'Teaching / Business'),
]

FORM_DIVISIONS = {
    'Form 1': ['A', 'B', 'K', 'L', 'M', 'N', 'P', 'S'],
    'Form 2': ['A', 'B', 'K', 'L', 'M', 'N', 'P', 'S'],
    'Form 3': ['A', 'B', 'K', 'L', 'M', 'N', 'P', 'S'],
    'Form 4': ['A', 'B', 'K', 'L', 'M', 'N', 'P', 'S'],
    'Form 5': ['A', 'B', 'K', 'L', 'M', 'N', 'P', 'S'],
    'Form 6': ['AS Jan', 'AS June', 'A2 Jan', 'A2 June'],
    'Form 7': ['AS Jan', 'AS June', 'A2 Jan', 'A2 June'],
}

SUBJECTS = [
    ('Computer Science', 'CS', 'Teaching / IT'),
    ('ICT', 'ICT', 'Teaching / IT'),
    ('Mathematics', 'MATH', 'Teaching / Maths'),
    ('Physics', 'PHY', 'Teaching / Sciences'),
    ('Chemistry', 'CHEM', 'Teaching / Sciences'),
    ('Biology', 'BIO', 'Teaching / Sciences'),
    ('Combined Science', 'CSCI', 'Teaching / Sciences'),
    ('English Language', 'ENG', 'Teaching / Languages'),
    ('Setswana', 'SET', 'Teaching / Languages'),
    ('French', 'FRE', 'Teaching / Languages'),
    ('Geography', 'GEO', 'Teaching / Humanities'),
    ('History', 'HIST', 'Teaching / Humanities'),
    ('Social Studies', 'SS', 'Teaching / Humanities'),
    ('Accounts', 'ACC', 'Teaching / Business'),
    ('Business', 'BUS', 'Teaching / Business'),
    ('Economics', 'ECON', 'Teaching / Business'),
    ('Art', 'ART', 'Teaching / Creatives'),
    ('Physical Education', 'PE', 'Teaching / Creatives'),
]

STUDENT_FIRST = ['Kagiso','Naledi','Thabo','Lesego','Mpho','Kefilwe','Tebogo','Boipelo',
                  'Olorato','Dintle','Kabo','Gaone','Onkemetse','Tshepiso','Bontle',
                  'Modiri','Refilwe','Tshepo','Lerato','Kgotso','Phenyo','Gaopalelwe',
                  'Mmoloki','Lorato','Tapiwa','Farai','Chido','Tatenda','Rudo','Tendai']
STUDENT_LAST = ['Moeti','Dube','Nkosi','Tau','Segoe','Gaone','Modise','Kgari','Molefi',
                 'Phiri','Seretse','Kgomo','Motswedi','Molaudi','Keabetswe','Seleke',
                 'Moseki','Gabaake','Maswabi','Mosweu','Thipe','Sebele','Morupisi','Dikgole']


class Command(BaseCommand):
    help = 'Seed the database with LKC School sample data'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding LKC School database...')

        # Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@lkc.ac.bw', 'admin123')
            self.stdout.write('  ✓ Admin user created (admin/admin123)')

        # Academic Years
        year_2025, _ = AcademicYear.objects.get_or_create(
            name='2025',
            defaults={'date_start': date(2025,1,1), 'date_end': date(2025,12,31), 'state': 'closed'}
        )
        year_2026, _ = AcademicYear.objects.get_or_create(
            name='2026',
            defaults={'date_start': date(2026,1,1), 'date_end': date(2026,12,31),
                      'state': 'active', 'is_current': True}
        )
        self.stdout.write('  ✓ Academic years')

        # Departments
        dept_map = {}
        for dept_name in set(d for _, _, d in SUBJECTS):
            code = dept_name.replace('Teaching / ', '').upper()[:10]
            dept, _ = Department.objects.get_or_create(name=dept_name, defaults={'code': code})
            dept_map[dept_name] = dept
        self.stdout.write('  ✓ Departments')

        # Subjects
        subject_map = {}
        for name, code, dept_name in SUBJECTS:
            subj, _ = Subject.objects.get_or_create(
                name=name, defaults={'code': code, 'department': dept_map.get(dept_name)}
            )
            subject_map[name] = subj
        self.stdout.write('  ✓ Subjects')

        # Forms & Divisions
        form_map = {}
        division_map = {}
        for seq, (form_name, divs) in enumerate(FORM_DIVISIONS.items(), 1):
            form, _ = SchoolForm.objects.get_or_create(name=form_name, defaults={'sequence': seq})
            form_map[form_name] = form
            for div_name in divs:
                div, _ = SchoolDivision.objects.get_or_create(name=div_name, form=form)
                division_map[(form_name, div_name)] = div
        self.stdout.write('  ✓ Forms & Divisions')

        # Teachers
        teacher_map = {}
        for teacher_name, code, dept_key, dept_full in TEACHER_DATA:
            dept = dept_map.get(dept_full)
            teacher, _ = FacultyInfo.objects.get_or_create(
                teacher_code=code,
                defaults={
                    'teacher_name': teacher_name,
                    'department': dept,
                    'joining_date': date(2020, 1, 15),
                    'work_email': f'{teacher_name.split(".")[1].strip().lower()}@lkc.ac.bw',
                    'state': 'active',
                }
            )
            teacher_map[teacher_name] = teacher
        self.stdout.write('  ✓ Teachers')

        # Parents
        parent_map = {}
        for i, last in enumerate(STUDENT_LAST[:20]):
            p_name = f'Mr/Mrs {last}'
            parent, _ = SchoolParent.objects.get_or_create(
                parent_name=p_name,
                defaults={'phone': f'+267 7{i} 000 {i:03d}', 'city': 'Gaborone'}
            )
            parent_map[last] = parent
        self.stdout.write('  ✓ Parents')

        # Students - generate ~120 across forms
        random.seed(42)
        students = []
        form_list = list(FORM_DIVISIONS.items())
        enrollment_counter = 1

        for form_name, divs in form_list:
            form = form_map[form_name]
            count = 8 if 'Form 6' in form_name or 'Form 7' in form_name else 20
            for i in range(count):
                first = random.choice(STUDENT_FIRST)
                last = random.choice(STUDENT_LAST)
                full_name = f'{first} {last}'
                div_name = random.choice(divs)
                division = division_map.get((form_name, div_name))
                parent = parent_map.get(last)
                enroll_no = f'STU{enrollment_counter:04d}'
                enrollment_counter += 1

                dob_year = 2026 - (int(form_name.split()[-1]) + 11)
                dob = date(dob_year, random.randint(1,12), random.randint(1,28))

                if not StudentInfo.objects.filter(enrollment_number=enroll_no).exists():
                    s = StudentInfo.objects.create(
                        student_full_name=full_name,
                        enrollment_number=enroll_no,
                        gender=random.choice(['male','female']),
                        date_of_birth=dob,
                        form=form,
                        division=division,
                        academic_year=year_2026,
                        enrollment_date=date(2026,1,8),
                        state='active',
                        city='Gaborone',
                        parent=parent,
                        guardian_name=f'{last} Sr.',
                        guardian_phone=f'+267 7{random.randint(1,9)} {random.randint(100,999)} {random.randint(100,999)}',
                    )
                    students.append(s)

        self.stdout.write(f'  ✓ Students ({len(students)} created)')

        # Exams
        exam1, _ = Exam.objects.get_or_create(
            exam_code='EXAM/0001',
            defaults={
                'exam_name': 'Mid-Term 1 2026',
                'form': form_map['Form 1'],
                'academic_year': year_2026,
                'exam_start_date': date(2026,3,1),
                'exam_end_date': date(2026,3,7),
                'state': 'done',
            }
        )
        exam2, _ = Exam.objects.get_or_create(
            exam_code='EXAM/0002',
            defaults={
                'exam_name': 'End of Term 1 2026',
                'form': form_map['Form 2'],
                'academic_year': year_2026,
                'exam_start_date': date(2026,4,20),
                'exam_end_date': date(2026,4,28),
                'state': 'confirmed',
            }
        )
        exam3, _ = Exam.objects.get_or_create(
            exam_code='EXAM/0003',
            defaults={
                'exam_name': 'Mid-Term 2 2026',
                'form': form_map['Form 3'],
                'academic_year': year_2026,
                'exam_start_date': date(2026,7,10),
                'exam_end_date': date(2026,7,17),
                'state': 'draft',
            }
        )
        self.stdout.write('  ✓ Exams')

        # Exam Results for Form 1 students in CS
        cs_subject = subject_map.get('Computer Science')
        math_subject = subject_map.get('Mathematics')
        cs_teacher = teacher_map.get('Ms. Makoni')
        math_teacher = teacher_map.get('Ms. Madzivanyika')

        form1_students = list(StudentInfo.objects.filter(form=form_map['Form 1'])[:20])
        for student in form1_students:
            marks = random.randint(35, 98)
            if not ExamResult.objects.filter(exam=exam1, student=student, subject=cs_subject).exists():
                ExamResult.objects.create(
                    exam=exam1, student=student, subject=cs_subject,
                    teacher=cs_teacher, division=student.division,
                    obtain_marks=marks, maximum_marks=100, minimum_marks=40,
                    state='done',
                )
            marks2 = random.randint(30, 95)
            if not ExamResult.objects.filter(exam=exam1, student=student, subject=math_subject).exists():
                ExamResult.objects.create(
                    exam=exam1, student=student, subject=math_subject,
                    teacher=math_teacher, division=student.division,
                    obtain_marks=marks2, maximum_marks=100, minimum_marks=40,
                    state='confirmed',
                )
        self.stdout.write('  ✓ Exam Results')

        # Attendance - last 5 days
        today = date.today()
        all_students = list(StudentInfo.objects.filter(state='active')[:30])
        for days_back in range(5):
            att_date = today - timedelta(days=days_back)
            if att_date.weekday() < 5:  # weekdays only
                for student in all_students:
                    roll = random.random()
                    state = 'present' if roll > 0.1 else ('absent' if roll > 0.05 else 'late')
                    Attendance.objects.get_or_create(
                        student=student,
                        date=att_date,
                        period='full_day',
                        defaults={
                            'state': state,
                            'academic_year': year_2026,
                            'teacher': cs_teacher,
                        }
                    )
        self.stdout.write('  ✓ Attendance records')

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write('   Login: admin / admin123')
        self.stdout.write('   API: http://localhost:8000/api/')

        # ── Assignments ────────────────────────────────────────────
        from apps.assignments.models import Assignment, AssignmentSubmission
        from django.utils import timezone as tz

        makoni = teacher_map.get('Ms. Makoni')
        madzivanyika = teacher_map.get('Ms. Madzivanyika')
        banda = teacher_map.get('Mr. Banda')

        assign_defs = [
            dict(title='Python Fundamentals Exercise',
                 description='Complete exercises covering variables, loops, and functions. Submit your .py source files.',
                 subject=subject_map.get('Computer Science'), form=form_map['Form 1'], division=None,
                 teacher=makoni, due_date=tz.now()+timedelta(days=7), total_marks=50,
                 submission_type='file', allow_late_submission=False, state='published'),
            dict(title='Algebra Problem Set 3',
                 description='Solve all 20 problems in Chapter 5. Show all working steps. Scanned PDF accepted.',
                 subject=subject_map.get('Mathematics'), form=form_map['Form 2'], division=None,
                 teacher=madzivanyika, due_date=tz.now()+timedelta(days=3), total_marks=100,
                 submission_type='file', allow_late_submission=True, state='published'),
            dict(title="Essay: Shakespeare's Use of Metaphor",
                 description='Write a 500-word analytical essay on how Shakespeare uses metaphor in Macbeth Act II.',
                 subject=subject_map.get('English Language'), form=form_map['Form 3'], division=None,
                 teacher=banda, due_date=tz.now()-timedelta(days=2), total_marks=30,
                 submission_type='both', allow_late_submission=False, state='closed'),
            dict(title='ICT Project: Database Design',
                 description='Design an ER diagram for a library management system. Include entities, relationships, and attributes.',
                 subject=subject_map.get('ICT'), form=form_map['Form 4'], division=None,
                 teacher=makoni, due_date=tz.now()+timedelta(days=14), total_marks=75,
                 submission_type='file', allow_late_submission=True, state='published'),
        ]

        created_assignments = []
        for a in assign_defs:
            obj, _ = Assignment.objects.get_or_create(title=a['title'], form=a['form'], defaults=a)
            created_assignments.append(obj)

        first_assign = created_assignments[0]
        for student in list(StudentInfo.objects.filter(form=form_map['Form 1']))[:5]:
            marks = random.randint(30, 50)
            AssignmentSubmission.objects.get_or_create(
                assignment=first_assign, student=student,
                defaults=dict(
                    submission_text=f'Submitted by {student.student_full_name}.',
                    status=random.choice(['submitted', 'graded']),
                    obtained_marks=marks if random.random() > 0.3 else None,
                    teacher_comment='Good work.' if random.random() > 0.5 else '',
                )
            )
        self.stdout.write('  \u2713 Assignments & submissions')
