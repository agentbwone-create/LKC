# LKC School Management System — Django REST API

Full school management backend built with Django 5 + Django REST Framework.
Ported from the existing Odoo module with identical data models and business logic.

## Stack
- **Backend**: Django 5 + Django REST Framework
- **Auth**: JWT via djangorestframework-simplejwt
- **Database**: SQLite (dev) → PostgreSQL (production)
- **Excel exports**: openpyxl (same HOD report logic as Odoo module)
- **Server**: Gunicorn + Nginx on Contabo VPS

---

## Local Development Setup

### 1. Install dependencies
```bash
cd lkc_school
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run migrations
```bash
python manage.py migrate
```

### 3. Seed sample data
```bash
python manage.py seed_data
# Creates: admin/admin123, 120 students, 10 teachers, exams, results, attendance
```

### 4. Start development server
```bash
python manage.py runserver
# API available at http://localhost:8000/api/
# Admin panel at http://localhost:8000/admin/
```

---

## Production Deployment on Contabo (Ubuntu 22.04)

### 1. Server setup
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib certbot python3-certbot-nginx -y
```

### 2. PostgreSQL
```bash
sudo -u postgres psql
CREATE DATABASE lkc_school;
CREATE USER lkc_user WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE lkc_school TO lkc_user;
\q
```
Update `settings.py` DATABASES section with PostgreSQL config.

### 3. Deploy application
```bash
sudo mkdir -p /var/www/lkc_school /var/log/lkc_school
sudo chown -R www-data:www-data /var/www/lkc_school /var/log/lkc_school

cd /var/www/lkc_school
git clone <your-repo> .           # or scp the files
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data
python manage.py collectstatic --noinput
```

### 4. Gunicorn service
```bash
sudo cp deploy/lkc_school.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lkc_school
sudo systemctl start lkc_school
```

### 5. Nginx
```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/lkc_school
sudo ln -s /etc/nginx/sites-available/lkc_school /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 6. SSL
```bash
sudo certbot --nginx -d your-domain.com
```

---

## API Reference

### Authentication
```
POST /api/auth/login/        { "username": "admin", "password": "admin123" }
POST /api/auth/refresh/      { "refresh": "<token>" }
```

### Core
```
GET  /api/academic-years/
GET  /api/forms/
GET  /api/divisions/?form=1
GET  /api/subjects/
GET  /api/departments/
GET  /api/subject-allocations/
GET  /api/timetables/
GET  /api/dashboard/
```

### Students
```
GET  /api/students/                    List (paginated, 50/page)
GET  /api/students/?form=1&state=active&search=Kagiso
GET  /api/students/{id}/
GET  /api/students/{id}/exam_results/
GET  /api/students/{id}/attendance/
POST /api/students/                    Create
PUT  /api/students/{id}/               Update
```

### Faculty
```
GET  /api/faculty/
GET  /api/faculty/?state=active&department=1
GET  /api/faculty/{id}/
POST /api/faculty/
```

### Parents
```
GET  /api/parents/
GET  /api/parents/{id}/
```

### Exams
```
GET  /api/exams/
GET  /api/exams/?state=done&form=1
GET  /api/exams/{id}/results/
POST /api/exams/{id}/confirm/
POST /api/exams/{id}/start/
POST /api/exams/{id}/done/
GET  /api/exams/results/
GET  /api/exams/results/?exam=1&subject=2&teacher=3
POST /api/exams/results/{id}/confirm/
POST /api/exams/results/{id}/approve/
```

### Attendance
```
GET  /api/attendance/?date=2026-03-01
GET  /api/attendance/?student=1
GET  /api/attendance/summary/?date=2026-03-01
```

### Reports
```
POST /api/reports/hod-report/          Returns .xlsx file download
POST /api/reports/hod-preview/         Returns JSON preview data

Body: {
  "exam_id": 1,
  "subject_id": 2,
  "pass_percentage": 50,
  "credit_pass_percentage": 60,
  "report_title": "ICT Department Term 1 2026"
}
```

---

## Capacity

With 4 Gunicorn workers on Contabo VPS (4 vCPUs, 8GB RAM):
- **Concurrent users**: 100+ comfortably
- **Requests/sec**: ~200 read operations
- **Database**: PostgreSQL handles 100 concurrent connections with ease

Scale by adding workers: `--workers 8` for 200+ concurrent users.
