from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db, bcrypt
from app.models import User, Student, Teacher, Course, Department, Enrollment

def log_activity(message, icon='📌'):
    from app.models import ActivityLog
    entry = ActivityLog(message=message, icon=icon)
    db.session.add(entry)
    db.session.commit()

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    from app.models import ActivityLog
    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    total_courses = Course.query.count()
    total_departments = Department.query.count()
    recent_activity = ActivityLog.query.order_by(
        ActivityLog.created_at.desc()).limit(8).all()
    return render_template('dashboard/admin.html',
                           total_students=total_students,
                           total_teachers=total_teachers,
                           total_courses=total_courses,
                           total_departments=total_departments,
                           recent_activity=recent_activity)

@admin.route('/students')
@login_required
@admin_required
def students():
    page = request.args.get('page', 1, type=int)
    all_students = Student.query.paginate(page=page, per_page=5, error_out=False)
    return render_template('admin/students.html', students=all_students)

@admin.route('/students/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    departments = Department.query.all()
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        student_number = request.form.get('student_number')
        department_id = request.form.get('department_id')
        year_level = request.form.get('year_level')

        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return render_template('admin/add_student.html', departments=departments)

        user = User(username=username, email=email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        student = Student(user_id=user.id, full_name=full_name,
                          student_number=student_number,
                          department_id=department_id, year_level=year_level)
        db.session.add(student)
        db.session.commit()
        log_activity(f'New student {full_name} was added', '👨‍🎓')
        from app.utils import send_welcome_student
        sent = send_welcome_student(email, full_name, username, password)
        if sent:
            flash('Student added and welcome email sent!', 'success')
        else:
            flash('Student added successfully!', 'success')
        return redirect(url_for('admin.students'))

    return render_template('admin/add_student.html', departments=departments)

@admin.route('/students/delete/<int:id>')
@login_required
@admin_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    user = User.query.get(student.user_id)
    db.session.delete(student)
    db.session.delete(user)
    db.session.commit()
    log_activity(f'Student {student.full_name} was deleted', '🗑️')
    flash('Student deleted.', 'success')
    return redirect(url_for('admin.students'))

@admin.route('/teachers')
@login_required
@admin_required
def teachers():
    page = request.args.get('page', 1, type=int)
    all_teachers = Teacher.query.paginate(page=page, per_page=5, error_out=False)
    return render_template('admin/teachers.html', teachers=all_teachers)

@admin.route('/teachers/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_teacher():
    departments = Department.query.all()
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        employee_number = request.form.get('employee_number')
        department_id = request.form.get('department_id')

        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return render_template('admin/add_teacher.html', departments=departments)

        user = User(username=username, email=email, role='teacher')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        teacher = Teacher(user_id=user.id, full_name=full_name,
                          employee_number=employee_number,
                          department_id=department_id)
        db.session.add(teacher)
        db.session.commit()
        log_activity(f'New teacher {full_name} was added', '👩‍🏫')
        flash('Teacher added successfully!', 'success')
        return redirect(url_for('admin.teachers'))

    return render_template('admin/add_teacher.html', departments=departments)

@admin.route('/courses')
@login_required
@admin_required
def courses():
    all_courses = Course.query.all()
    return render_template('admin/courses.html', courses=all_courses)

@admin.route('/courses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_course():
    departments = Department.query.all()
    teachers = Teacher.query.all()
    if request.method == 'POST':
        course = Course(
            course_code=request.form.get('course_code'),
            course_name=request.form.get('course_name'),
            credits=request.form.get('credits'),
            semester=request.form.get('semester'),
            teacher_id=request.form.get('teacher_id'),
            department_id=request.form.get('department_id')
        )
        db.session.add(course)
        db.session.commit()
        log_activity(f'New course {request.form.get("course_name")} was added', '📚')
        flash('Course added successfully!', 'success')
        return redirect(url_for('admin.courses'))

    return render_template('admin/add_course.html', departments=departments, teachers=teachers)

@admin.route('/departments', methods=['GET', 'POST'])
@login_required
@admin_required
def departments():
    if request.method == 'POST':
        name = request.form.get('name')
        dept = Department(name=name)
        db.session.add(dept)
        db.session.commit()
        flash('Department added!', 'success')
    all_departments = Department.query.all()
    return render_template('admin/departments.html', departments=all_departments)

@admin.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    departments = Department.query.all()

    if request.method == 'POST':
        student.full_name = request.form.get('full_name')
        student.student_number = request.form.get('student_number')
        student.year_level = request.form.get('year_level')
        student.department_id = request.form.get('department_id')

        # Update login email
        user = User.query.get(student.user_id)
        user.email = request.form.get('email')
        user.username = request.form.get('username')

        # Only update password if a new one was entered
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)

        db.session.commit()
        log_activity(f'Student {student.full_name} was updated', '✏️')
        flash('Student updated successfully!', 'success')
        return redirect(url_for('admin.students'))

    user = User.query.get(student.user_id)
    return render_template('admin/edit_student.html',
                           student=student, user=user, departments=departments)


@admin.route('/teachers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    departments = Department.query.all()

    if request.method == 'POST':
        teacher.full_name = request.form.get('full_name')
        teacher.employee_number = request.form.get('employee_number')
        teacher.department_id = request.form.get('department_id')

        user = User.query.get(teacher.user_id)
        user.email = request.form.get('email')
        user.username = request.form.get('username')

        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)

        db.session.commit()
        log_activity(f'Teacher {teacher.full_name} was updated', '✏️')
        flash('Teacher updated successfully!', 'success')
        return redirect(url_for('admin.teachers'))

    user = User.query.get(teacher.user_id)
    return render_template('admin/edit_teacher.html',
                           teacher=teacher, user=user, departments=departments)

@admin.route('/analytics')
@login_required
@admin_required
def analytics():
    from app.models import Grade, Enrollment, Attendance, Course

    # Grade distribution across all students
    grades = Grade.query.all()
    grade_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    for g in grades:
        grade_counts[g.letter_grade] += 1

    # Enrollment per course
    courses = Course.query.all()
    course_names = [c.course_code for c in courses]
    course_enrollments = [Enrollment.query.filter_by(course_id=c.id).count() for c in courses]

    # Attendance overview
    total_attendance = Attendance.query.count()
    present = Attendance.query.filter_by(status='present').count()
    absent = Attendance.query.filter_by(status='absent').count()
    late = Attendance.query.filter_by(status='late').count()

    # Students per department
    from app.models import Department
    departments = Department.query.all()
    dept_names = [d.name for d in departments]
    dept_counts = [Student.query.filter_by(department_id=d.id).count() for d in departments]

    return render_template('admin/analytics.html',
        grade_counts=grade_counts,
        course_names=course_names,
        course_enrollments=course_enrollments,
        present=present, absent=absent, late=late,
        dept_names=dept_names, dept_counts=dept_counts
    )