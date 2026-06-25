# 🎓 EduTrack — Student Management System

A full-stack web application built with **Flask** and **SQLite** for managing students, teachers, courses, attendance, and grades with role-based access control.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Flask](https://img.shields.io/badge/Flask-3.1.3-lightgrey)
![SQLite](https://img.shields.io/badge/Database-SQLite-green)
![Bootstrap](https://img.shields.io/badge/UI-Bootstrap%205-purple)

---

## ✨ Features

### 🔐 Authentication
- Role-based login system (Admin, Teacher, Student)
- Secure password hashing with Flask-Bcrypt
- Session management with Flask-Login

### 👨‍💼 Admin
- Dashboard with animated statistics
- Manage Students, Teachers, Courses, Departments
- Full CRUD with live search & filter

### 👩‍🏫 Teacher
- View assigned courses
- Mark student attendance (Present / Absent / Late)
- Enter and update grades

### 👨‍🎓 Student
- Personal dashboard with GPA display
- Browse and enroll in courses
- View attendance percentage per course
- View grades with letter grade calculation
- Download official PDF transcript

### 🎨 UI/UX
- Animated login page with glassmorphism card
- Dark / Light mode toggle
- Sidebar navigation
- Count-up animations on stats
- Fully responsive with Bootstrap 5

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | SQLite, Flask-SQLAlchemy |
| Auth | Flask-Login, Flask-Bcrypt |
| Frontend | Bootstrap 5, Bootstrap Icons, Vanilla JS |
| PDF | ReportLab |

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/edutrack.git
cd edutrack
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python run.py
```

### 5. Seed sample data (optional but recommended)
```bash
python seed.py
```

Visit **http://127.0.0.1:5000**

---

## 🔑 Default Login Credentials

After running `seed.py`:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@edutrack.com | admin123 |
| Teacher | teacher1@edutrack.com | teacher123 |
| Student | student1@edutrack.com | student123 |

---

## 📁 Project Structure

```
edutrack/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── student.py
│   │   └── teacher.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard/
│   │   └── admin/, student/, teacher/
│   └── static/
│       └── style.css
├── seed.py
├── run.py
├── config.py
└── requirements.txt
```

---

## 📊 Grade Calculation

| Component | Weight |
|-----------|--------|
| Assignment | 20% |
| Midterm | 30% |
| Final Exam | 50% |

| Grade | Points | Range |
|-------|--------|-------|
| A | 4.0 | 90-100 |
| B | 3.0 | 80-89 |
| C | 2.0 | 70-79 |
| D | 1.0 | 60-69 |
| F | 0.0 | Below 60 |

---

## 📄 License
MIT License — feel free to use this project for learning and portfolio purposes.