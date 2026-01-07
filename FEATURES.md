# SAE_104 - Features Overview

## 📋 Complete Feature List

### 1. **View All Students** (Main Page)
- **URL**: `/`
- **Method**: GET
- **Features**:
  - Displays all students in a responsive table
  - Shows: ID, Name, Email, Age, Major, Created At
  - Edit button for each student
  - Delete button with confirmation dialog
  - Modern purple gradient design
  - Navigation buttons to add new students

### 2. **Add New Student**
- **URL**: `/add`
- **Method**: GET/POST
- **Features**:
  - Form with fields: Name*, Email*, Age, Major
  - Required field validation (Name and Email)
  - Email format validation
  - HTML/XSS input sanitization
  - CSRF protection
  - Success/error flash messages
  - Cancel button to return to main page

### 3. **Edit Student**
- **URL**: `/edit/<student_id>`
- **Method**: GET/POST
- **Features**:
  - Pre-filled form with current student data
  - Same validation as Add form
  - Updates specific student by ID
  - CSRF protection
  - Success/error flash messages
  - Cancel button to return to main page

### 4. **Delete Student**
- **URL**: `/delete/<student_id>`
- **Method**: POST
- **Features**:
  - JavaScript confirmation dialog
  - CSRF protection
  - Permanent deletion from database
  - Success/error flash messages
  - Automatic redirect to main page

## 🔒 Security Features

1. **CSRF Protection**
   - All POST forms include CSRF tokens
   - Flask-WTF provides automatic validation

2. **Input Validation**
   - Email format validation using regex
   - Required field checking
   - Age range validation (1-150)

3. **XSS Prevention**
   - HTML escaping using markupsafe.escape()
   - Prevents script injection attacks

4. **SQL Injection Prevention**
   - Parameterized queries for all database operations
   - mysql-connector-python handles escaping

5. **Configuration Security**
   - Environment variables for sensitive data
   - Secret key for session management
   - Debug mode controlled via environment

## 🎨 User Interface

### Design Elements
- **Color Scheme**: Purple gradient (667eea to 764ba2)
- **Responsive**: Works on mobile and desktop
- **Modern**: Clean, professional appearance
- **Icons**: Emoji icons for visual appeal
- **Feedback**: Flash messages for all actions

### Pages Layout

#### Main Page (index.html)
```
┌─────────────────────────────────────────┐
│  📚 Student Management System           │
│  Python + MySQL + HTML Interface        │
├─────────────────────────────────────────┤
│  [🏠 View All] [➕ Add Student]         │
├─────────────────────────────────────────┤
│  📋 All Students                        │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ ID │ Name │ Email │ Age │ Major│   │
│  ├─────────────────────────────────┤   │
│  │ 1  │ John │ j@... │ 20  │ CS   │   │
│  │    │      │       │     │[Edit]│   │
│  │    │      │       │     │[Del] │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

#### Add/Edit Page
```
┌─────────────────────────────────────────┐
│  📚 Student Management System           │
│  Python + MySQL + HTML Interface        │
├─────────────────────────────────────────┤
│  [🏠 View All] [➕ Add Student]         │
├─────────────────────────────────────────┤
│  ➕ Add New Student                     │
│                                         │
│  Name *                                 │
│  [_________________________]            │
│                                         │
│  Email *                                │
│  [_________________________]            │
│                                         │
│  Age                                    │
│  [_________________________]            │
│                                         │
│  Major                                  │
│  [_________________________]            │
│                                         │
│  [💾 Save] [❌ Cancel]                  │
└─────────────────────────────────────────┘
```

## 📊 Database Operations

### CREATE
- Insert new student with name, email, age, major
- Auto-generated ID and timestamps

### READ
- Fetch all students for main page
- Fetch single student for edit page
- Results returned as dictionaries

### UPDATE
- Modify existing student data
- Updates timestamp automatically

### DELETE
- Remove student by ID
- Permanent deletion

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup database
mysql -u root -p < database_setup.sql

# 3. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 4. Run application
python app.py

# 5. Open browser
# Navigate to http://localhost:5000
```

## 📦 Dependencies

- **Flask 3.0.0**: Web framework
- **mysql-connector-python 9.1.0**: MySQL database driver
- **python-dotenv 1.0.0**: Environment variable management
- **Flask-WTF 1.2.1**: CSRF protection
- **email-validator 2.1.0**: Email validation

## ✅ Quality Assurance

- ✓ No syntax errors in Python code
- ✓ All templates validate successfully
- ✓ CSRF protection on all forms
- ✓ Input validation and sanitization
- ✓ CodeQL security scan: 0 alerts
- ✓ Parameterized SQL queries
- ✓ Environment-based configuration
- ✓ Comprehensive error handling
