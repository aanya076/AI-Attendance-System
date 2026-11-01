import sqlite3
from datetime import datetime

DATABASE = "attendance.db"


def connect_database():
    connection = sqlite3.connect(
        DATABASE,
        timeout=30
    )
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    with connect_database() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_no TEXT UNIQUE NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT NOT NULL,
                UNIQUE(student_id, date)
            )
        """)


def add_student(name, roll_no):
    with connect_database() as connection:
        connection.execute(
            """
            INSERT INTO students (name, roll_no)
            VALUES (?, ?)
            """,
            (name.strip(), roll_no.strip())
        )


def get_students():
    with connect_database() as connection:
        return connection.execute(
            "SELECT * FROM students ORDER BY name"
        ).fetchall()


def get_student_by_roll(roll_no):
    with connect_database() as connection:
        return connection.execute(
            "SELECT * FROM students WHERE roll_no = ?",
            (roll_no.strip(),)
        ).fetchone()


def mark_attendance(student_id):
    current_time = datetime.now()
    date = current_time.strftime("%Y-%m-%d")
    time = current_time.strftime("%H:%M:%S")

    with connect_database() as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO attendance
            (student_id, date, time, status)
            VALUES (?, ?, ?, ?)
            """,
            (student_id, date, time, "Present")
        )


def get_attendance():
    with connect_database() as connection:
        return connection.execute(
            """
            SELECT
                students.name,
                students.roll_no,
                attendance.date,
                attendance.time,
                attendance.status
            FROM attendance
            JOIN students
                ON attendance.student_id = students.id
            ORDER BY
                attendance.date DESC,
                attendance.time DESC
            """
        ).fetchall()


create_tables()