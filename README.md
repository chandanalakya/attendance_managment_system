# SAMS2 - Student Attendance Management System

**Project ID:** P18  
**Course:** UE23CS341A  
**Team:** Visionsoft

## 🚀 Quick Start

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

## 🔐 Security Features

- Secure authentication with password hashing
- Account lockout after 5 failed attempts
- 15-minute session timeout
- Comprehensive audit logging
- TLS encryption indicators

## 📊 User Requirements Coverage

✅ **20/20 User Stories Implemented**
- Student Requirements (US-S01 to US-S06)
- Faculty Requirements (US-F01 to US-F07)  
- Admin Requirements (US-A01 to US-A06)
- Security Requirements (US-Sec01 to US-Sec07)

## 🧪 Testing & Quality

```bash
make test       # Run tests
make coverage   # Coverage analysis
make lint       # Code quality
make security   # Security scan
```

## 📁 Project Structure

```
SAMS2/
├── sams_complete.py         # Main application
├── database/               # Database schemas
├── src/                   # Core modules
├── tests/                 # Test suite
├── .github/workflows/     # CI/CD pipeline
└── requirements.txt       # Dependencies
```

## 🔧 Default Credentials

- **Admin**: admin/admin123
- **Faculty**: faculty1/faculty123
- **Student**: PES2UG23CS143/student123

## 👥 Team Visionsoft

- [@PES2UG23CS143](https://github.com/PES2UG23CS143) - Scrum Master
- [@PES2UG23CS165EC](https://github.com/PES2UG23CS165EC) - Developer
- [@PES2UG23CS160](https://github.com/PES2UG23CS160) - Developer
- [@PES2UG23-CS157](https://github.com/PES2UG23-CS157) - Developer

---
**Status**: ✅ Production Ready  
**Institution**: PES University  
**Academic Year**: 2025