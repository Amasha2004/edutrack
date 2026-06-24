from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Teacher, Course, Enrollment, Attendance, Grade
from datetime import date

teacher = Blueprint('teacher', __name__, url_prefix='/teacher')

def teacher_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'teacher':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@teacher.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    profile = Teacher.query.filter_by(user_id=current_user.id).first()
    courses = Course.query.filter_by(teacher_id=profile.id).all()
    return render_template('dashboard/teacher.html', profile=profile, courses=courses)

@teacher.route('/courses/<int:course_id>/attendance', methods=['GET', 'POST'])
@login_required
@teacher_required
def attendance(course_id):
    course = Course.query.get_or_404(course_id)
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()

    if request.method == 'POST':
        today = date.today()
        for e in enrollments:
            status = request.form.get(f'status_{e.id}', 'absent')
            record = Attendance(enrollment_id=e.id, date=today, status=status)
            db.session.add(record)
        db.session.commit()
        flash('Attendance saved!', 'success')
        return redirect(url_for('teacher.dashboard'))

    return render_template('teacher/attendance.html', course=course, enrollments=enrollments)

@teacher.route('/courses/<int:course_id>/grades', methods=['GET', 'POST'])
@login_required
@teacher_required
def grades(course_id):
    course = Course.query.get_or_404(course_id)
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()

    if request.method == 'POST':
        for e in enrollments:
            grade = Grade.query.filter_by(enrollment_id=e.id).first()
            if not grade:
                grade = Grade(enrollment_id=e.id)
                db.session.add(grade)
            grade.assignment = float(request.form.get(f'assignment_{e.id}', 0))
            grade.midterm = float(request.form.get(f'midterm_{e.id}', 0))
            grade.final_exam = float(request.form.get(f'final_{e.id}', 0))
        db.session.commit()
        flash('Grades saved!', 'success')
        return redirect(url_for('teacher.dashboard'))

    return render_template('teacher/grades.html', course=course, enrollments=enrollments)