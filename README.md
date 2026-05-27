# SAMS2 - Student Attendance Management System

**Project ID:** P18  
**Course:** UE23CS341A  
**Team:** Visionsoft

##  Quick Start

### Prerequisites
- Python 3.11+
- MySQL 8.0+

### Setup
```bash
# Install dependencies
make install

# Setup database
mysql -u root -p -e "CREATE DATABASE sams2;"

# Configure environment
cp .env.example .env
# Edit .env with your MySQL credentials

# Initialize database
make setup

# Run application
make run
```

## 🎯 Features

### Student Dashboard
- Overall attendance percentage with status indicators
- Subject-wise attendance breakdown
- Daily attendance history with date filtering
- Real-time data synchronization

### Faculty Dashboard  
- Real-time attendance marking for classes
- Edit attendance with mandatory justification
- Attendance analytics and trend charts
- Export reports in CSV format

### Admin Dashboard
- Defaulter management with configurable thresholds
- Comprehensive audit log monitoring
- System-wide analytics and dashboards
- User management and security settings

##  Security Features

- Secure authentication with password hashing
- Account lockout after 5 failed attempts
- 15-minute session timeout
- Comprehensive audit logging
- TLS encryption indicators

## 📊 User Requirements Coverage

 **20/20 User Stories Implemented**
- Student Requirements (US-S01 to US-S06)
- Faculty Requirements (US-F01 to US-F07)  
- Admin Requirements (US-A01 to US-A06)
- Security Requirements (US-Sec01 to US-Sec07)

##  Testing & Quality

```bash
make test       # Run tests
make coverage   # Coverage analysis
make lint       # Code quality
make security   # Security scan
```

##  Project Structure

```
SAMS2/
├── sams_complete.py         # Main application
├── database/               # Database schemas
├── src/                   # Core modules
├── tests/                 # Test suite
├── .github/workflows/     # CI/CD pipeline
└── requirements.txt       # Dependencies
```

##  Default Credentials

- **Admin**: admin/admin123
- **Faculty**: faculty1/faculty123
- **Student**: PES2UG23CS143/student123

##  Team Visionsoft

- [@PES2UG23CS143](https://github.com/PES2UG23CS143) - Scrum Master
- [@PES2UG23CS165EC](https://github.com/PES2UG23CS165EC) - Developer
- [@PES2UG23CS160](https://github.com/PES2UG23CS160) - Developer
- [@PES2UG23-CS157](https://github.com/PES2UG23-CS157) - Developer

---
**Status**:  Production Ready  
**Institution**: PES University  
**Academic Year**: 2025
# 📚 Student Attendance Management System

A comprehensive attendance management platform built using **Python and Streamlit** that enables educational institutions to efficiently manage student attendance, user authentication, dashboards, reporting, and audit logging.

The system supports role-based access for administrators, faculty members, and students while providing secure attendance tracking, export functionality, and automated reporting.

---

#  Features

##  Secure Authentication System

* User registration and login
* Role-based access control
* Session management
* Secure password handling

##  Faculty Dashboard

* Mark student attendance
* Manage attendance records
* Generate attendance reports
* Export reports to CSV and PDF

##  Student Dashboard

* View attendance status
* Track attendance percentage
* Access attendance history

##  Admin Dashboard

* Manage users and roles
* Monitor attendance logs
* System administration controls
* Audit log tracking

##  Reporting & Analytics

* Attendance summaries
* Attendance percentage calculations
* CSV export functionality
* PDF report generation

##  Audit Logging

* Tracks important system actions
* Activity monitoring support
* Improved transparency and accountability

##  Testing & Coverage

* Unit testing support
* Integration testing support
* High test coverage implementation
* Automated testing workflow

---

#  Tech Stack

| Technology                  | Purpose                    |
| --------------------------- | -------------------------- |
| Python                      | Backend Development        |
| Streamlit                   | Frontend Interface         |
| SQLite / Database Layer     | Data Storage               |
| Pytest                      | Unit & Integration Testing |
| Report Generation Libraries | PDF & CSV Exports          |
| VS Code                     | Development Environment    |

---

# Project Structure

```bash
student-attendance-management-system/
│
├── app.py
├── requirements.txt
├── README.md
│
├── config/
│   └── settings.py
│
├── src/
│   ├── auth/
│   │   ├── authentication.py
│   │   └── signup.py
│   │
│   ├── dashboards/
│   │   ├── admin.py
│   │   ├── faculty.py
│   │   └── student.py
│   │
│   ├── models/
│   │   ├── attendance.py
│   │   ├── audit_log.py
│   │   └── user.py
│   │
│   ├── components/
│   │   └── sidebar.py
│   │
│   └── utils/
│       ├── db.py
│       ├── export_csv.py
│       ├── export_pdf.py
│       ├── security.py
│       └── session.py
│
├── tests/
│   ├── integration/
│   └── unit/
│
└── htmlcov/
```

---

#  System Architecture

The system follows a modular architecture:

1. Users authenticate through the login system
2. Role-based dashboards are loaded dynamically
3. Faculty manages attendance records
4. Students view attendance analytics
5. Admin monitors system activities and logs
6. Reports can be exported as CSV or PDF
7. Audit logs maintain activity tracking

---

#  Installation & Setup

## 1️ Clone the Repository

```bash
git clone https://github.com/your-username/attendance-management-system.git
cd attendance-management-system
```

---

## 2️ Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3️ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️ Configure Environment Variables

Create a `.env` file if required for application settings.

Example:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
```

---

## 5️ Run the Application

```bash
streamlit run app.py
```

The application will open in your browser.

---

#  Core Modules

## 🔐 Authentication Module

* User signup
* Login/logout
* Session handling
* Role verification

## 👨‍🏫 Faculty Module

* Attendance marking
* Attendance editing
* Student attendance management

## 👨‍🎓 Student Module

* Attendance viewing
* Attendance percentage tracking
* Attendance history

## 🛠 Admin Module

* User administration
* Activity monitoring
* Audit log management

## 📤 Export Module

* CSV export support
* PDF report generation
* Downloadable attendance records

## 🧪 Testing Module

* Unit tests
* Integration tests
* Coverage reports

---

#  Security Features

* Secure authentication system
* Session management
* Audit logging
* Role-based authorization
* Protected dashboard access

---

#  Testing & Quality Assurance

The project includes:

* Extensive unit testing
* Integration testing
* Code coverage reports
* Automated test execution

Run tests using:

```bash
pytest
```

Generate coverage report:

```bash
pytest --cov
```

---

#  Functional Requirements

| ID   | Requirement           |
| ---- | --------------------- |
| FR1  | User Authentication   |
| FR2  | Attendance Management |
| FR3  | Student Dashboard     |
| FR4  | Faculty Dashboard     |
| FR5  | Admin Dashboard       |
| FR6  | Attendance Reports    |
| FR7  | CSV/PDF Export        |
| FR8  | Audit Logging         |
| FR9  | Session Management    |
| FR10 | Testing & Validation  |

---

#  Future Enhancements

* Face recognition attendance system
* QR-code attendance tracking
* Mobile application support
* Real-time notifications
* Advanced analytics dashboard
* Cloud deployment support
* AI-based attendance prediction
* Multi-institution support

---

#  Learning Outcomes

This project demonstrates:

* Full-stack application development
* Modular software architecture
* Role-based authentication systems
* Attendance management workflows
* Report generation techniques
* Automated testing practices
* Security and session management

---

#  Team Members

* Chandana
* VisionSoft Team

---

#  License

This project is developed for educational and academic purposes.

---

# 🌟 Acknowledgements

Special thanks to the open-source community and all technologies used in building this platform.
