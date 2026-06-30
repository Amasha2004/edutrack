from flask_mail import Message
from app import mail
from flask import render_template_string

def send_welcome_student(student_email, student_name, username, password):
    msg = Message(
        subject='Welcome to EduTrack! 🎓',
        recipients=[student_email]
    )
    msg.html = f'''
    <div style="font-family:sans-serif; max-width:600px; margin:0 auto; padding:40px; background:#f8fafc; border-radius:16px;">
        <div style="text-align:center; margin-bottom:32px;">
            <h1 style="color:#1a73e8; font-size:2rem;">🎓 EduTrack</h1>
            <p style="color:#718096;">Student Management System</p>
        </div>
        <div style="background:white; border-radius:12px; padding:32px; box-shadow:0 4px 20px rgba(0,0,0,0.06);">
            <h2 style="color:#1a202c;">Welcome, {student_name}! 👋</h2>
            <p style="color:#4a5568; line-height:1.7;">
                Your student account has been created successfully. Here are your login credentials:
            </p>
            <div style="background:#f0f7ff; border-radius:10px; padding:20px; margin:20px 0;">
                <p style="margin:0; color:#2d3748;"><b>Email:</b> {student_email}</p>
                <p style="margin:8px 0 0; color:#2d3748;"><b>Password:</b> {password}</p>
            </div>
            <p style="color:#718096; font-size:0.9rem;">
                Please change your password after your first login.
            </p>
            <a href="http://127.0.0.1:5000/login"
               style="display:inline-block; margin-top:16px; padding:14px 28px;
                      background:linear-gradient(135deg, #1a73e8, #7c3aed);
                      color:white; border-radius:10px; text-decoration:none; font-weight:700;">
                Login to EduTrack →
            </a>
        </div>
        <p style="text-align:center; color:#a0aec0; margin-top:24px; font-size:0.85rem;">
            EduTrack — Empowering Education
        </p>
    </div>
    '''
    try:
        mail.send(msg)
        return True
    except:
        return False


def send_grade_notification(student_email, student_name, course_name, letter_grade, gpa):
    msg = Message(
        subject=f'Grades Posted for {course_name} 📊',
        recipients=[student_email]
    )
    msg.html = f'''
    <div style="font-family:sans-serif; max-width:600px; margin:0 auto; padding:40px; background:#f8fafc; border-radius:16px;">
        <div style="text-align:center; margin-bottom:32px;">
            <h1 style="color:#1a73e8;">🎓 EduTrack</h1>
        </div>
        <div style="background:white; border-radius:12px; padding:32px; box-shadow:0 4px 20px rgba(0,0,0,0.06);">
            <h2 style="color:#1a202c;">Grades Updated! 📊</h2>
            <p style="color:#4a5568;">Hi {student_name}, your grades have been updated.</p>
            <div style="background:#f0f7ff; border-radius:10px; padding:20px; margin:20px 0;">
                <p style="margin:0; color:#2d3748;"><b>Course:</b> {course_name}</p>
                <p style="margin:8px 0 0; color:#2d3748;"><b>Grade:</b> {letter_grade}</p>
                <p style="margin:8px 0 0; color:#2d3748;"><b>Current GPA:</b> {gpa}</p>
            </div>
            <a href="http://127.0.0.1:5000/student/grades"
               style="display:inline-block; margin-top:16px; padding:14px 28px;
                      background:linear-gradient(135deg, #1a73e8, #7c3aed);
                      color:white; border-radius:10px; text-decoration:none; font-weight:700;">
                View My Grades →
            </a>
        </div>
    </div>
    '''
    try:
        mail.send(msg)
        return True
    except:
        return False