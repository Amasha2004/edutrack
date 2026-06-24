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