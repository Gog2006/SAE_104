# SAE_104 - Student Management System

A basic Python-SQL project with an HTML interface to add, view, and update information in a MySQL/phpMyAdmin database.

## Features

- 📋 **View Students**: Display all students from the database in a clean table format
- ➕ **Add Students**: Add new student records with name, email, age, and major
- ✏️ **Edit Students**: Update existing student information
- 🗑️ **Delete Students**: Remove student records from the database
- 🎨 **Modern UI**: Clean and responsive HTML interface with attractive styling

## Technologies Used

- **Backend**: Python 3.x with Flask web framework
- **Database**: MySQL/MariaDB (compatible with phpMyAdmin)
- **Frontend**: HTML5 with embedded CSS
- **Database Connector**: mysql-connector-python

## Project Structure

```
SAE_104/
├── app.py                  # Main Flask application
├── database.py             # Database connection and operations
├── database_setup.sql      # SQL script to create database and tables
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment configuration
├── templates/             # HTML templates
│   ├── base.html         # Base template with styling
│   ├── index.html        # View all students
│   ├── add.html          # Add new student
│   └── edit.html         # Edit existing student
└── README.md             # This file
```

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- MySQL or MariaDB server
- phpMyAdmin (optional, for database management)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Gog2006/SAE_104.git
cd SAE_104
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Database

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and update with your database credentials:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=sae_104_db
DB_PORT=3306

# Important: Set a strong secret key for production
SECRET_KEY=your-strong-random-secret-key-here
```

**Note**: For production deployment, generate a strong random SECRET_KEY using:
```bash
python -c "import os; print(os.urandom(24).hex())"
```

### Step 4: Create Database and Tables

Run the SQL setup script in MySQL or phpMyAdmin:

**Option 1: Using MySQL command line:**
```bash
mysql -u root -p < database_setup.sql
```

**Option 2: Using phpMyAdmin:**
1. Open phpMyAdmin in your browser
2. Click on "Import" tab
3. Choose the `database_setup.sql` file
4. Click "Go"

### Step 5: Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Usage

### Viewing Students

- Navigate to `http://localhost:5000/` to see all students in the database
- Students are displayed in a table with their ID, name, email, age, major, and creation date

### Adding a New Student

1. Click the "➕ Add Student" button
2. Fill in the form with student information:
   - Name (required)
   - Email (required)
   - Age (optional)
   - Major (optional)
3. Click "💾 Save Student"
4. You'll be redirected to the main page with a success message

### Editing a Student

1. On the main page, click the "✏️ Edit" button next to any student
2. Modify the information in the form
3. Click "💾 Update Student"
4. You'll be redirected to the main page with a success message

### Deleting a Student

1. On the main page, click the "🗑️ Delete" button next to any student
2. Confirm the deletion in the popup dialog
3. The student will be removed from the database

## Database Schema

The application uses a simple `students` table:

| Column     | Type         | Description                      |
|------------|--------------|----------------------------------|
| id         | INT          | Primary key (auto-increment)     |
| name       | VARCHAR(100) | Student name (required)          |
| email      | VARCHAR(100) | Student email (required)         |
| age        | INT          | Student age (optional)           |
| major      | VARCHAR(100) | Student major (optional)         |
| created_at | TIMESTAMP    | Record creation timestamp        |
| updated_at | TIMESTAMP    | Record update timestamp          |

## Troubleshooting

### Database Connection Error

If you get a connection error:
1. Verify MySQL/MariaDB is running
2. Check your `.env` file has correct credentials
3. Ensure the database exists (run `database_setup.sql`)

### Port Already in Use

If port 5000 is already in use, modify the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to desired port
```

### Module Not Found Error

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Contributing

This is an educational project for SAE_104. Feel free to fork and modify for your own learning purposes.

## License

This project is open source and available under the MIT License. 
