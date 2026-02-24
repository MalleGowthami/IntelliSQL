"""
database_setup.py
Creates and populates a sample SQLite database for the Intelligent SQL Query project.
Contains tables: employees, departments, projects, salaries
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "company.db")


def create_database():
    """Create the SQLite database with sample tables and data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ── Drop existing tables ──
    cursor.executescript("""
        DROP TABLE IF EXISTS salaries;
        DROP TABLE IF EXISTS project_assignments;
        DROP TABLE IF EXISTS projects;
        DROP TABLE IF EXISTS employees;
        DROP TABLE IF EXISTS departments;
    """)

    # ── Create tables ──
    cursor.executescript("""
        CREATE TABLE departments (
            department_id   INTEGER PRIMARY KEY,
            department_name TEXT    NOT NULL,
            location        TEXT    NOT NULL
        );

        CREATE TABLE employees (
            employee_id     INTEGER PRIMARY KEY,
            first_name      TEXT    NOT NULL,
            last_name       TEXT    NOT NULL,
            email           TEXT    UNIQUE NOT NULL,
            hire_date       DATE    NOT NULL,
            department_id   INTEGER,
            job_title       TEXT    NOT NULL,
            FOREIGN KEY (department_id) REFERENCES departments(department_id)
        );

        CREATE TABLE projects (
            project_id      INTEGER PRIMARY KEY,
            project_name    TEXT    NOT NULL,
            start_date      DATE   NOT NULL,
            end_date        DATE,
            budget          REAL   NOT NULL,
            status          TEXT   NOT NULL DEFAULT 'Active'
        );

        CREATE TABLE salaries (
            salary_id       INTEGER PRIMARY KEY,
            employee_id     INTEGER NOT NULL,
            salary_amount   REAL    NOT NULL,
            effective_date  DATE    NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        );

        CREATE TABLE project_assignments (
            assignment_id   INTEGER PRIMARY KEY,
            employee_id     INTEGER NOT NULL,
            project_id      INTEGER NOT NULL,
            role            TEXT    NOT NULL,
            assigned_date   DATE    NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        );
    """)

    # ── Insert sample data ──

    departments = [
        (1, "Engineering", "Building A, Floor 3"),
        (2, "Marketing", "Building B, Floor 1"),
        (3, "Human Resources", "Building A, Floor 1"),
        (4, "Finance", "Building C, Floor 2"),
        (5, "Data Science", "Building A, Floor 4"),
    ]
    cursor.executemany(
        "INSERT INTO departments VALUES (?, ?, ?)", departments
    )

    employees = [
        (1, "Aarav", "Sharma", "aarav.sharma@company.com", "2021-03-15", 1, "Software Engineer"),
        (2, "Priya", "Patel", "priya.patel@company.com", "2020-07-20", 1, "Senior Software Engineer"),
        (3, "Rahul", "Gupta", "rahul.gupta@company.com", "2022-01-10", 2, "Marketing Analyst"),
        (4, "Sneha", "Reddy", "sneha.reddy@company.com", "2019-11-05", 3, "HR Manager"),
        (5, "Vikram", "Singh", "vikram.singh@company.com", "2023-02-28", 1, "Junior Developer"),
        (6, "Ananya", "Iyer", "ananya.iyer@company.com", "2020-09-14", 4, "Financial Analyst"),
        (7, "Rohan", "Mehta", "rohan.mehta@company.com", "2021-06-01", 5, "Data Scientist"),
        (8, "Kavya", "Nair", "kavya.nair@company.com", "2022-08-22", 5, "ML Engineer"),
        (9, "Arjun", "Kumar", "arjun.kumar@company.com", "2018-04-12", 1, "Tech Lead"),
        (10, "Divya", "Joshi", "divya.joshi@company.com", "2023-05-17", 2, "Content Strategist"),
        (11, "Manish", "Verma", "manish.verma@company.com", "2021-11-30", 4, "Accountant"),
        (12, "Pooja", "Agarwal", "pooja.agarwal@company.com", "2020-02-14", 3, "Recruiter"),
        (13, "Siddharth", "Rao", "siddharth.rao@company.com", "2019-08-25", 1, "DevOps Engineer"),
        (14, "Neha", "Desai", "neha.desai@company.com", "2022-12-01", 5, "Data Analyst"),
        (15, "Amit", "Choudhary", "amit.choudhary@company.com", "2023-09-10", 2, "Marketing Manager"),
    ]
    cursor.executemany(
        "INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?)", employees
    )

    projects = [
        (1, "Cloud Migration", "2024-01-15", "2024-12-31", 500000.00, "Active"),
        (2, "Customer Analytics", "2023-06-01", "2024-06-30", 250000.00, "Active"),
        (3, "Mobile App Redesign", "2023-09-01", "2024-03-31", 180000.00, "Completed"),
        (4, "AI Chatbot", "2024-03-01", None, 350000.00, "Active"),
        (5, "ERP System Upgrade", "2022-01-01", "2023-12-31", 750000.00, "Completed"),
    ]
    cursor.executemany(
        "INSERT INTO projects VALUES (?, ?, ?, ?, ?, ?)", projects
    )

    salaries = [
        (1, 1, 85000.00, "2024-01-01"),
        (2, 2, 120000.00, "2024-01-01"),
        (3, 3, 65000.00, "2024-01-01"),
        (4, 4, 95000.00, "2024-01-01"),
        (5, 5, 55000.00, "2024-01-01"),
        (6, 6, 78000.00, "2024-01-01"),
        (7, 7, 110000.00, "2024-01-01"),
        (8, 8, 105000.00, "2024-01-01"),
        (9, 9, 140000.00, "2024-01-01"),
        (10, 10, 60000.00, "2024-01-01"),
        (11, 11, 72000.00, "2024-01-01"),
        (12, 12, 68000.00, "2024-01-01"),
        (13, 13, 115000.00, "2024-01-01"),
        (14, 14, 75000.00, "2024-01-01"),
        (15, 15, 90000.00, "2024-01-01"),
    ]
    cursor.executemany(
        "INSERT INTO salaries VALUES (?, ?, ?, ?)", salaries
    )

    assignments = [
        (1, 1, 1, "Backend Developer", "2024-01-20"),
        (2, 2, 1, "Lead Developer", "2024-01-20"),
        (3, 9, 1, "Project Manager", "2024-01-15"),
        (4, 13, 1, "DevOps Lead", "2024-02-01"),
        (5, 7, 2, "Lead Data Scientist", "2023-06-01"),
        (6, 8, 2, "ML Engineer", "2023-06-15"),
        (7, 14, 2, "Data Analyst", "2023-07-01"),
        (8, 5, 3, "Frontend Developer", "2023-09-01"),
        (9, 1, 4, "AI Developer", "2024-03-01"),
        (10, 8, 4, "ML Engineer", "2024-03-15"),
        (11, 7, 4, "Data Scientist", "2024-04-01"),
    ]
    cursor.executemany(
        "INSERT INTO project_assignments VALUES (?, ?, ?, ?, ?)", assignments
    )

    conn.commit()
    conn.close()
    print(f"Database created successfully at: {DB_PATH}")


def get_schema_info():
    """Return a formatted string describing the database schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = cursor.fetchall()

    schema_info = []
    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        col_details = []
        for col in columns:
            col_id, name, col_type, not_null, default_val, pk = col
            constraints = []
            if pk:
                constraints.append("PRIMARY KEY")
            if not_null:
                constraints.append("NOT NULL")
            constraint_str = f" ({', '.join(constraints)})" if constraints else ""
            col_details.append(f"    - {name} {col_type}{constraint_str}")

        schema_info.append(f"Table: {table_name}\n" + "\n".join(col_details))

    conn.close()
    return "\n\n".join(schema_info)


if __name__ == "__main__":
    create_database()
    print("\n--- Database Schema ---")
    print(get_schema_info())
