# Student attendance management system

**Project ID:** P18  
**Course:** UE23CS341A  
**Academic Year:** 2025  
**Semester:** 5th Sem  
**Campus:** EC  
**Branch:** CSE  
**Section:** C  
**Team:** Visionsoft

## 📋 Project Description

An app like the app we have at PESU

This repository contains the source code and documentation for the Student attendance management system project, developed as part of the UE23CS341A course at PES University.

## 🧑‍💻 Development Team (Visionsoft)

- [@PES2UG23CS143](https://github.com/PES2UG23CS143) - Scrum Master
- [@PES2UG23CS165EC](https://github.com/PES2UG23CS165EC) - Developer Team
- [@PES2UG23CS160](https://github.com/PES2UG23CS160) - Developer Team
- [@PES2UG23-CS157](https://github.com/PES2UG23-CS157) - Developer Team

## 👨‍🏫 Teaching Assistant

- [@nikitha-0704](https://github.com/nikitha-0704)
- [@samwilson129](https://github.com/samwilson129)
- [@harshamogra](https://github.com/harshamogra)

## 👨‍⚖️ Faculty Supervisor

- [@sudeeparoydey](https://github.com/sudeeparoydey)


## 🚀 Getting Started

### Prerequisites
- [List your prerequisites here]

### Installation
1. Clone the repository
   ```bash
   git clone https://github.com/pestechnology/PESU_EC_CSE_C_P18_Student_attendance_management_system_Visionsoft.git
   cd PESU_EC_CSE_C_P18_Student_attendance_management_system_Visionsoft
   ```

2. Install dependencies
   ```bash
   # Add your installation commands here
   ```

3. Run the application
   ```bash
   # Add your run commands here
   ```

##  Project Structure

```
PESU_EC_CSE_C_P18_Student_attendance_management_system_Visionsoft/
├── src/                 # Source code
├── docs/               # Documentation
├── tests/              # Test files
├── .github/            # GitHub workflows and templates
├── README.md          # This file
└── ...
```

## 🛠️ Development Guidelines

### Branching Strategy
- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches

### Commit Messages
Follow conventional commit format:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test-related changes

### Code Review Process
1. Create feature branch from `develop`
2. Make changes and commit
3. Create Pull Request to `develop`
4. Request review from team members
5. Merge after approval

##  Documentation

- [API Documentation](docs/api.md)
- [User Guide](docs/user-guide.md)
- [Developer Guide](docs/developer-guide.md)

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

# SAMS2 — Student Attendance Management System (Audit Logging)

Stack: **Python + Streamlit**, SQLite, `schema.sql`, PyTest, GitHub Actions CI.

## Features
- Logs every attendance **Add/Edit/Delete** with timestamp, user ID, and IP.
- Audit logs stored **separately** and **immutable** (DB triggers block update/delete).
- Admin can filter by **date**, **user**, **course** in the Streamlit UI.
- Export logs to **CSV** or **PDF**.
- Attempts to modify logs are **blocked**, **logged as security events**, and surfaced in UI via error toast.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The first run creates `sams2.db` using `schema.sql`.

## Tests
```bash
pytest -q
```

## CI
See `.github/workflows/ci.yml` — runs lint + tests on every push/PR.


##  License

This project is developed for educational purposes as part of the PES University UE23CS341A curriculum.

---

**Course:** UE23CS341A  
**Institution:** PES University  
**Academic Year:** 2025  
**Semester:** 5th Sem
