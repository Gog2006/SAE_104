-- Create database
CREATE DATABASE IF NOT EXISTS sae_104_db;
USE sae_104_db;

-- Create a sample table for storing student information
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    age INT,
    major VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert some sample data
INSERT INTO students (name, email, age, major) VALUES
('John Doe', 'john.doe@example.com', 20, 'Computer Science'),
('Jane Smith', 'jane.smith@example.com', 22, 'Mathematics'),
('Bob Johnson', 'bob.johnson@example.com', 21, 'Physics');
