create database symbi;
use symbi;

create table departments(
	dept_id int auto_increment primary key,
    dept_name varchar(100) unique not null
    );
    
CREATE TABLE employees (
    emp_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    hire_date DATE NOT NULL,
    salary DECIMAL(10,2) NOT NULL,
    dept_id INT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE SET NULL
);
-- Step 4: Create Salaries Table
CREATE TABLE salaries (
    salary_id INT AUTO_INCREMENT PRIMARY KEY,
    emp_id INT,
    salary DECIMAL(10,2) NOT NULL,
    bonus DECIMAL(10,2) DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);
    
INSERT INTO departments (dept_name) VALUES 
('HR'), 
('IT'), 
('Finance'), 
('Marketing');

INSERT INTO employees (first_name, last_name, email, phone, hire_date, salary, dept_id) VALUES 
('Alice', 'Johnson', 'alice@symbiosis.com', '9876543210', '2023-05-10', 60000, 2),
('Bob', 'Smith', 'bob@symbiosis.com', '9876543211', '2022-08-15', 55000, 1),
('Charlie', 'Brown', 'charlie@symbiosis.com', '9876543212', '2021-06-20', 70000, 3);

INSERT INTO salaries (emp_id, salary, bonus) VALUES 
(1, 60000, 5000),
(2, 55000, 4000),
(3, 70000, 6000);

-- Step 10: Verify Data
SELECT * FROM employees;
SELECT * FROM departments;
SELECT * FROM salaries;