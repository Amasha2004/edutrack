from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm
from flask import make_response
import io
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Student, Course, Enrollment, Attendance, Grade

student = Blueprint('student', __name__, url_prefix='/student')

def student_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@student.route('/dashboard')
@login_required
@student_required
def dashboard():
    profile = Student.query.filter_by(user_id=current_user.id).first()
    enrollments = Enrollment.query.filter_by(student_id=profile.id).all()

    # Calculate GPA
    total_points = 0
    total_credits = 0
    for e in enrollments:
        if e.grade:
            credits = e.course.credits
            total_points += e.grade.grade_points * credits
            total_credits += credits
    gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0

    return render_template('dashboard/student.html',
                           profile=profile,
                           enrollments=enrollments,
                           gpa=gpa)

@student.route('/courses')
@login_required
@student_required
def courses():
    profile = Student.query.filter_by(user_id=current_user.id).first()
    enrolled_ids = [e.course_id for e in profile.enrollments]
    available = Course.query.filter(Course.id.notin_(enrolled_ids)).all()
    return render_template('student/courses.html', courses=available, enrolled_ids=enrolled_ids)

@student.route('/enroll/<int:course_id>')
@login_required
@student_required
def enroll(course_id):
    profile = Student.query.filter_by(user_id=current_user.id).first()
    already = Enrollment.query.filter_by(student_id=profile.id, course_id=course_id).first()
    if already:
        flash('Already enrolled in this course.', 'warning')
    else:
        enrollment = Enrollment(student_id=profile.id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        flash('Enrolled successfully!', 'success')
    return redirect(url_for('student.courses'))

@student.route('/attendance')
@login_required
@student_required
def attendance():
    profile = Student.query.filter_by(user_id=current_user.id).first()
    enrollments = Enrollment.query.filter_by(student_id=profile.id).all()
    attendance_data = []
    for e in enrollments:
        records = Attendance.query.filter_by(enrollment_id=e.id).all()
        total = len(records)
        present = len([r for r in records if r.status == 'present'])
        percentage = round((present / total) * 100, 1) if total > 0 else 0
        attendance_data.append({
            'course': e.course.course_name,
            'total': total,
            'present': present,
            'percentage': percentage
        })
    return render_template('student/attendance.html', attendance_data=attendance_data)

@student.route('/grades')
@login_required
@student_required
def grades():
    profile = Student.query.filter_by(user_id=current_user.id).first()
    enrollments = Enrollment.query.filter_by(student_id=profile.id).all()
    return render_template('student/grades.html', enrollments=enrollments)

@student.route('/transcript/download')
@login_required
@student_required
def download_transcript():
    profile = Student.query.filter_by(user_id=current_user.id).first()
    enrollments = Enrollment.query.filter_by(student_id=profile.id).all()

    # Calculate GPA
    total_points = 0
    total_credits = 0
    for e in enrollments:
        if e.grade:
            credits = e.course.credits
            total_points += e.grade.grade_points * credits
            total_credits += credits
    gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0

    # Build PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = ParagraphStyle('title', fontSize=22, fontName='Helvetica-Bold',
                                  textColor=colors.HexColor('#1a73e8'), spaceAfter=6)
    sub_style = ParagraphStyle('sub', fontSize=11, fontName='Helvetica',
                                textColor=colors.grey, spaceAfter=4)
    normal = ParagraphStyle('normal', fontSize=11, fontName='Helvetica', spaceAfter=4)

    elements.append(Paragraph('🎓 EduTrack', title_style))
    elements.append(Paragraph('Official Academic Transcript', sub_style))
    elements.append(Spacer(1, 0.5*cm))

    # Student Info
    elements.append(Paragraph(f'<b>Student Name:</b> {profile.full_name}', normal))
    elements.append(Paragraph(f'<b>Student Number:</b> {profile.student_number}', normal))
    elements.append(Paragraph(f'<b>Department:</b> {profile.department.name if profile.department else "N/A"}', normal))
    elements.append(Paragraph(f'<b>Year Level:</b> {profile.year_level}', normal))
    elements.append(Spacer(1, 0.5*cm))

    # Grades Table
    table_data = [['Course', 'Code', 'Credits', 'Assignment', 'Midterm', 'Final', 'Total', 'Grade']]

    for e in enrollments:
        if e.grade:
            table_data.append([
                e.course.course_name,
                e.course.course_code,
                str(e.course.credits),
                f'{e.grade.assignment:.1f}',
                f'{e.grade.midterm:.1f}',
                f'{e.grade.final_exam:.1f}',
                f'{e.grade.total:.1f}',
                e.grade.letter_grade
            ])
        else:
            table_data.append([
                e.course.course_name,
                e.course.course_code,
                str(e.course.credits),
                '-', '-', '-', '-', 'N/A'
            ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a73e8')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f7ff')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6')),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))

    elements.append(Paragraph('<b>Academic Record</b>', styles['Heading2']))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(table)
    elements.append(Spacer(1, 0.5*cm))

    # GPA Summary
    gpa_color = '#2ecc71' if gpa >= 3.0 else '#f39c12' if gpa >= 2.0 else '#e74c3c'
    gpa_style = ParagraphStyle('gpa', fontSize=14, fontName='Helvetica-Bold',
                                textColor=colors.HexColor(gpa_color))
    elements.append(Paragraph(f'Cumulative GPA: {gpa} / 4.0', gpa_style))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(Paragraph(f'Total Credits: {total_credits}', normal))
    elements.append(Spacer(1, 1*cm))
    elements.append(Paragraph('_' * 40, normal))
    elements.append(Paragraph('Authorized by EduTrack Academic Office', sub_style))

    doc.build(elements)
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=transcript_{profile.student_number}.pdf'
    return response