from app import create_app, db
from app.models import User, Student, Teacher, Course, Department, Enrollment, Grade, Attendance
from datetime import date

app = create_app()

with app.app_context():
    # Clear existing data
    print("Clearing old data...")
    Attendance.query.delete()
    Grade.query.delete()
    Enrollment.query.delete()
    Course.query.delete()
    Student.query.delete()
    Teacher.query.delete()
    Department.query.delete()
    User.query.filter(User.role != 'admin').delete()
    db.session.commit()

    # Departments
    print("Creating departments...")
    dept1 = Department(name='Computer Science')
    dept2 = Department(name='Mathematics')
    dept3 = Department(name='Physics')
    db.session.add_all([dept1, dept2, dept3])
    db.session.flush()

    # Teachers
    print("Creating teachers...")
    teachers_data = [
        ('teacher1', 'teacher1@edutrack.com', 'Dr. Alice Johnson', 'T001', dept1.id),
        ('teacher2', 'teacher2@edutrack.com', 'Prof. Bob Smith',   'T002', dept2.id),
        ('teacher3', 'teacher3@edutrack.com', 'Dr. Carol White',   'T003', dept3.id),
    ]
    teachers = []
    for username, email, full_name, emp_no, dept_id in teachers_data:
        user = User(username=username, email=email, role='teacher')
        user.set_password('teacher123')
        db.session.add(user)
        db.session.flush()
        teacher = Teacher(user_id=user.id, full_name=full_name,
                         employee_number=emp_no, department_id=dept_id)
        db.session.add(teacher)
        db.session.flush()
        teachers.append(teacher)

    # Courses
    print("Creating courses...")
    courses_data = [
        ('CS101', 'Introduction to Programming', 3, 'Fall 2024', teachers[0].id, dept1.id),
        ('CS201', 'Data Structures',             3, 'Fall 2024', teachers[0].id, dept1.id),
        ('MA101', 'Calculus I',                  4, 'Fall 2024', teachers[1].id, dept2.id),
        ('MA201', 'Linear Algebra',              3, 'Fall 2024', teachers[1].id, dept2.id),
        ('PH101', 'General Physics',             4, 'Fall 2024', teachers[2].id, dept3.id),
    ]
    courses = []
    for code, name, credits, sem, teacher_id, dept_id in courses_data:
        course = Course(course_code=code, course_name=name, credits=credits,
                       semester=sem, teacher_id=teacher_id, department_id=dept_id)
        db.session.add(course)
        db.session.flush()
        courses.append(course)

    # Students
    print("Creating students...")
    students_data = [
        ('student1', 'student1@edutrack.com', 'Emma Davis',   'S001', dept1.id, 1),
        ('student2', 'student2@edutrack.com', 'James Wilson', 'S002', dept1.id, 2),
        ('student3', 'student3@edutrack.com', 'Sofia Garcia', 'S003', dept2.id, 1),
        ('student4', 'student4@edutrack.com', 'Liam Brown',   'S004', dept2.id, 3),
        ('student5', 'student5@edutrack.com', 'Mia Taylor',   'S005', dept3.id, 2),
    ]
    students = []
    for username, email, full_name, s_no, dept_id, year in students_data:
        user = User(username=username, email=email, role='student')
        user.set_password('student123')
        db.session.add(user)
        db.session.flush()
        student = Student(user_id=user.id, full_name=full_name,
                         student_number=s_no, department_id=dept_id, year_level=year)
        db.session.add(student)
        db.session.flush()
        students.append(student)

    # Enroll students in courses
    print("Creating enrollments...")
    enrollments_map = {
        0: [0, 1, 2],  # Emma → CS101, CS201, MA101
        1: [0, 1, 4],  # James → CS101, CS201, PH101
        2: [2, 3],     # Sofia → MA101, MA201
        3: [2, 3, 4],  # Liam  → MA101, MA201, PH101
        4: [4, 0],     # Mia   → PH101, CS101
    }
    enrollments = []
    for student_idx, course_indices in enrollments_map.items():
        for course_idx in course_indices:
            e = Enrollment(student_id=students[student_idx].id,
                          course_id=courses[course_idx].id)
            db.session.add(e)
            db.session.flush()
            enrollments.append((student_idx, course_idx, e))

    # Grades
    print("Creating grades...")
    import random
    for student_idx, course_idx, enrollment in enrollments:
        grade = Grade(
            enrollment_id=enrollment.id,
            assignment=random.randint(70, 100),
            midterm=random.randint(65, 100),
            final_exam=random.randint(60, 100)
        )
        db.session.add(grade)

    # Attendance
    print("Creating attendance...")
    statuses = ['present', 'present', 'present', 'absent', 'late']
    class_dates = [
        date(2024, 9, 2), date(2024, 9, 9), date(2024, 9, 16),
        date(2024, 9, 23), date(2024, 9, 30), date(2024, 10, 7),
        date(2024, 10, 14), date(2024, 10, 21)
    ]
    for student_idx, course_idx, enrollment in enrollments:
        for d in class_dates:
            att = Attendance(
                enrollment_id=enrollment.id,
                date=d,
                status=random.choice(statuses)
            )
            db.session.add(att)

    db.session.commit()
    print("\n✅ Seed data created successfully!")
    print("=" * 40)
    print("Admin:    admin@edutrack.com / admin123")
    print("Teachers: teacher1@edutrack.com / teacher123")
    print("          teacher2@edutrack.com / teacher123")
    print("          teacher3@edutrack.com / teacher123")
    print("Students: student1@edutrack.com / student123")
    print("          student2@edutrack.com / student123")
    print("          (and student3, 4, 5)")
    print("=" * 40)