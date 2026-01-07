from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from database import Database
import os
import re

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24).hex())

# Enable CSRF protection
csrf = CSRFProtect(app)

# Initialize database
db = Database()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(text):
    """Basic input sanitization to prevent XSS"""
    if text is None:
        return None
    # Remove potential HTML/script tags and their content
    text = re.sub(r'<script[^>]*>.*?</script>', '', str(text), flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]*>', '', text)
    return text.strip()

@app.before_request
def before_request():
    """Connect to database before each request"""
    if not db.connection or not db.connection.is_connected():
        if not db.connect():
            flash('Database connection failed. Please check your configuration.', 'error')

@app.teardown_appcontext
def teardown_db(exception=None):
    """Close database connection after each request"""
    pass  # We keep the connection open for better performance

@app.route('/')
def index():
    """Home page - display all students"""
    students = db.fetch_all("SELECT * FROM students ORDER BY id DESC")
    return render_template('index.html', students=students)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    """Add new student"""
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name'))
        email = sanitize_input(request.form.get('email'))
        age = request.form.get('age')
        major = sanitize_input(request.form.get('major'))
        
        # Validate input
        if not name or not email:
            flash('Name and email are required!', 'error')
            return redirect(url_for('add_student'))
        
        # Validate email format
        if not validate_email(email):
            flash('Invalid email format!', 'error')
            return redirect(url_for('add_student'))
        
        # Insert into database
        query = "INSERT INTO students (name, email, age, major) VALUES (%s, %s, %s, %s)"
        params = (name, email, age if age else None, major)
        
        if db.execute_query(query, params):
            flash('Student added successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Error adding student!', 'error')
    
    return render_template('add.html')

@app.route('/edit/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    """Edit existing student"""
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name'))
        email = sanitize_input(request.form.get('email'))
        age = request.form.get('age')
        major = sanitize_input(request.form.get('major'))
        
        # Validate input
        if not name or not email:
            flash('Name and email are required!', 'error')
            return redirect(url_for('edit_student', student_id=student_id))
        
        # Validate email format
        if not validate_email(email):
            flash('Invalid email format!', 'error')
            return redirect(url_for('edit_student', student_id=student_id))
        
        # Update in database
        query = "UPDATE students SET name=%s, email=%s, age=%s, major=%s WHERE id=%s"
        params = (name, email, age if age else None, major, student_id)
        
        if db.execute_query(query, params):
            flash('Student updated successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Error updating student!', 'error')
    
    # Get student data
    student = db.fetch_one("SELECT * FROM students WHERE id=%s", (student_id,))
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('index'))
    
    return render_template('edit.html', student=student)

@app.route('/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    """Delete student"""
    query = "DELETE FROM students WHERE id=%s"
    
    if db.execute_query(query, (student_id,)):
        flash('Student deleted successfully!', 'success')
    else:
        flash('Error deleting student!', 'error')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))
    app.run(debug=debug_mode, host=host, port=port)
