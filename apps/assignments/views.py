from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from django.http import HttpResponse
from .models import Assignment, AssignmentSubmission
from .serializers import (
    AssignmentSerializer, AssignmentListSerializer,
    SubmissionSerializer, SubmissionCreateSerializer, GradeSubmissionSerializer,
)


def _is_admin(request):
    return request.user.is_staff or request.user.is_superuser


def _get_teacher(request):
    """Return FacultyInfo for the logged-in user, or None."""
    try:
        return request.user.faculty_profile
    except Exception:
        return None


def _get_student(request):
    """Return StudentInfo for the logged-in user, or None."""
    try:
        return request.user.student_profile
    except Exception:
        return None


class AssignmentViewSet(viewsets.ModelViewSet):
    """
    Handles all assignment CRUD + custom actions.

    Role behaviour:
      - Admin / unauthenticated-but-staff: see all
      - Teacher: see own assignments + assignments for forms they teach
      - Student: see assignments for their own form/division
    """
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'teacher__teacher_name']
    ordering_fields = ['due_date', 'created_at', 'title']

    def get_serializer_class(self):
        if self.action == 'list':
            return AssignmentListSerializer
        return AssignmentSerializer

    def get_queryset(self):
        qs = Assignment.objects.select_related(
            'subject', 'form', 'division', 'teacher', 'academic_year'
        ).prefetch_related('submissions')

        # Filter by query params
        p = self.request.query_params
        if p.get('form'):
            qs = qs.filter(form_id=p['form'])
        if p.get('division'):
            qs = qs.filter(division_id=p['division'])
        if p.get('subject'):
            qs = qs.filter(subject_id=p['subject'])
        if p.get('state'):
            qs = qs.filter(state=p['state'])
        if p.get('teacher'):
            qs = qs.filter(teacher_id=p['teacher'])

        # Role-based filtering (when authentication is active)
        if self.request.user.is_authenticated:
            if _is_admin(self.request):
                return qs  # admin sees all
            teacher = _get_teacher(self.request)
            if teacher:
                return qs.filter(teacher=teacher)
            student = _get_student(self.request)
            if student and student.form:
                qs = qs.filter(form=student.form, state='published')
                if student.division:
                    qs = qs.filter(
                        models.Q(division=student.division) | models.Q(division__isnull=True)
                    )
                return qs

        return qs

    def perform_create(self, serializer):
        # Auto-assign teacher from logged-in user, or allow explicit assignment
        teacher = _get_teacher(self.request)
        if teacher:
            serializer.save(teacher=teacher)
        else:
            serializer.save()

    # ── Custom actions ────────────────────────────────────────────

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """Teacher: get all submissions for an assignment, including non-submitters."""
        assignment = self.get_object()

        # Get all students in the target class
        from apps.students.models import StudentInfo
        students_qs = StudentInfo.objects.filter(form=assignment.form, state='active')
        if assignment.division:
            students_qs = students_qs.filter(division=assignment.division)

        # Build rich response: submitted + not-submitted
        submitted = {s.student_id: s for s in assignment.submissions.select_related(
            'student', 'graded_by'
        )}

        result = []
        for student in students_qs:
            sub = submitted.get(student.id)
            if sub:
                result.append({
                    'student_id': student.id,
                    'student_name': student.student_full_name,
                    'enrollment_number': student.enrollment_number,
                    'division': str(student.division) if student.division else '',
                    'submitted': True,
                    'submission_id': sub.id,
                    'submitted_at': sub.submitted_at.isoformat(),
                    'is_late': sub.is_late,
                    'status': sub.status,
                    'obtained_marks': sub.obtained_marks,
                    'teacher_comment': sub.teacher_comment,
                    'has_file': bool(sub.submission_file),
                    'text_preview': sub.submission_text[:120] if sub.submission_text else '',
                })
            else:
                overdue = assignment.is_overdue
                result.append({
                    'student_id': student.id,
                    'student_name': student.student_full_name,
                    'enrollment_number': student.enrollment_number,
                    'division': str(student.division) if student.division else '',
                    'submitted': False,
                    'submission_id': None,
                    'submitted_at': None,
                    'is_late': False,
                    'status': 'overdue' if overdue else 'not_submitted',
                    'obtained_marks': None,
                    'teacher_comment': '',
                    'has_file': False,
                    'text_preview': '',
                })

        return Response({
            'assignment': AssignmentListSerializer(assignment).data,
            'total_students': len(result),
            'submitted_count': sum(1 for r in result if r['submitted']),
            'graded_count': sum(1 for r in result if r['status'] == 'graded'),
            'submissions': result,
        })

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Student: submit an assignment."""
        assignment = self.get_object()

        # Check for existing submission
        student = _get_student(request)
        existing = None
        if student:
            existing = AssignmentSubmission.objects.filter(
                assignment=assignment, student=student
            ).first()

        if existing:
            return Response(
                {'detail': 'You have already submitted this assignment.',
                 'submission_id': existing.id,
                 'allow_overwrite': True},
                status=status.HTTP_409_CONFLICT
            )

        serializer = SubmissionCreateSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        # Determine if late
        sub_status = 'late' if assignment.is_overdue else 'submitted'
        sub = serializer.save(
            assignment=assignment,
            student=student,
            status=sub_status,
        )
        return Response(SubmissionSerializer(sub, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def resubmit(self, request, pk=None):
        """Student: overwrite existing submission."""
        assignment = self.get_object()
        student = _get_student(request)

        if not student:
            return Response({'detail': 'Student profile not found.'}, status=400)

        existing = AssignmentSubmission.objects.filter(
            assignment=assignment, student=student
        ).first()

        if not existing:
            return Response({'detail': 'No existing submission to overwrite.'}, status=400)

        if assignment.is_overdue and not assignment.allow_late_submission:
            return Response({'detail': 'Past due date, late submissions not allowed.'}, status=400)

        serializer = SubmissionCreateSerializer(
            existing, data=request.data, partial=True, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        sub_status = 'late' if assignment.is_overdue else 'submitted'
        sub = serializer.save(status=sub_status)
        return Response(SubmissionSerializer(sub, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        assignment = self.get_object()
        assignment.state = 'published'
        assignment.save()
        return Response({'status': 'published'})

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        assignment = self.get_object()
        assignment.state = 'closed'
        assignment.save()
        return Response({'status': 'closed'})


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    Direct submission access: teacher grading, student viewing own.
    """
    serializer_class = SubmissionSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = AssignmentSubmission.objects.select_related(
            'assignment', 'student', 'graded_by'
        )
        p = self.request.query_params
        if p.get('assignment'):
            qs = qs.filter(assignment_id=p['assignment'])
        if p.get('student'):
            qs = qs.filter(student_id=p['student'])
        if p.get('status'):
            qs = qs.filter(status=p['status'])
        return qs

    @action(detail=True, methods=['post', 'patch'])
    def grade(self, request, pk=None):
        """Teacher: grade a submission."""
        submission = self.get_object()
        serializer = GradeSubmissionSerializer(submission, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        sub = serializer.save(
            graded_by=_get_teacher(request),
            graded_at=timezone.now(),
            status='graded',
        )
        return Response(SubmissionSerializer(sub, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def my_submissions(self, request):
        """Student: get all own submissions."""
        student = _get_student(request)
        if not student:
            return Response([])
        subs = AssignmentSubmission.objects.filter(student=student).select_related(
            'assignment__form', 'assignment__subject', 'assignment__teacher'
        )
        return Response(SubmissionSerializer(subs, many=True, context={'request': request}).data)


# Need Q import for complex queries
from django.db import models as dj_models
# Patch the get_queryset to use proper Q objects
_orig = AssignmentViewSet.get_queryset

def _patched_get_queryset(self):
    from django.db.models import Q
    qs = Assignment.objects.select_related(
        'subject', 'form', 'division', 'teacher', 'academic_year'
    ).prefetch_related('submissions')

    p = self.request.query_params
    if p.get('form'):
        qs = qs.filter(form_id=p['form'])
    if p.get('division'):
        qs = qs.filter(division_id=p['division'])
    if p.get('subject'):
        qs = qs.filter(subject_id=p['subject'])
    if p.get('state'):
        qs = qs.filter(state=p['state'])
    if p.get('teacher'):
        qs = qs.filter(teacher_id=p['teacher'])

    if self.request.user.is_authenticated:
        if _is_admin(self.request):
            return qs
        teacher = _get_teacher(self.request)
        if teacher:
            return qs.filter(teacher=teacher)
        student = _get_student(self.request)
        if student and student.form:
            qs = qs.filter(form=student.form, state='published')
            if student.division:
                qs = qs.filter(
                    Q(division=student.division) | Q(division__isnull=True)
                )
            return qs

    return qs

AssignmentViewSet.get_queryset = _patched_get_queryset
